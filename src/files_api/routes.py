"""Define API routes."""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Request,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object
from files_api.schemas import (
    PUT_FILE_EXAMPLES,
    FileMetadata,
    GetFilesQueryParams,
    GetFilesResponse,
    PutFileResponse,
)
from files_api.settings import Settings
from files_api.utils import object_exists_response

ROUTER = APIRouter(tags=["Files"])

##################
# --- Routes --- #
##################


@ROUTER.put(
    "/v1/files/{file_path:path}",
    responses={
        status.HTTP_200_OK: {"model": PutFileResponse, **PUT_FILE_EXAMPLES["200"]},
        status.HTTP_201_CREATED: {"model": PutFileResponse, **PUT_FILE_EXAMPLES["201"]},
    },
)
async def upload_file(request: Request, file_path: str, file: UploadFile, response: Response) -> PutFileResponse:
    """Upload a file."""
    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name

    file_contents: bytes = await file.read()

    response_message, status_code = object_exists_response(s3_bucket_name, file_path)
    response.status_code = status_code

    upload_s3_object(
        bucket_name=s3_bucket_name, object_key=file_path, file_content=file_contents, content_type=file.content_type
    )

    return PutFileResponse(file_path=file_path, message=response_message)


@ROUTER.get("/v1/files")
async def list_files(
    request: Request,
    query_params: GetFilesQueryParams = Depends(),
) -> GetFilesResponse:
    """List files with pagination."""
    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name
    if query_params.page_token:
        obj_page = fetch_s3_objects_using_page_token(
            bucket_name=s3_bucket_name, continuation_token=query_params.page_token, max_keys=query_params.page_size
        )
    elif query_params.directory:
        obj_page = fetch_s3_objects_metadata(
            bucket_name=s3_bucket_name, prefix=query_params.directory, max_keys=query_params.page_size
        )
    else:
        obj_page = fetch_s3_objects_metadata(bucket_name=s3_bucket_name, max_keys=query_params.page_size)

    return GetFilesResponse(
        files=[
            FileMetadata(file_path=file["Key"], last_modified=file["LastModified"], size_bytes=file["Size"])
            for file in obj_page[0]
        ],
        next_page_token=obj_page[1],
    )


@ROUTER.head(
    "/v1/files/{file_path:path}",
    responses={
        status.HTTP_200_OK: {
            "headers": {
                "Content-Type": {
                    "description": "The [MIME type](https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types) of the file.",
                    "example": "text/plain",
                    "schema": {"type": "string"},
                },
                "Content-Length": {
                    "description": "The size of the file in bytes.",
                    "example": 1024,
                    "schema": {"type": "integer"},
                },
                "Last-Modified": {
                    "description": "The last modified date of the file.",
                    "example": "Thu, 01 Jan 2022 00:00:00 GMT",
                    "schema": {"type": "string", "format": "date-time"},
                },
            }
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "File not found for the given `file_path`.",
        },
    },
)
async def get_file_metadata(request: Request, file_path: str, response: Response) -> Response:
    """
    Retrieve file metadata.

    Note: by convention, HEAD requests MUST NOT return a body in the response.
    """
    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name

    object_exists = object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")

    obj = fetch_s3_object(bucket_name=s3_bucket_name, object_key=file_path)

    response.status_code = status.HTTP_200_OK
    response.headers["Content-Type"] = obj["ContentType"]
    response.headers["Content-Length"] = str(obj["ContentLength"])
    response.headers["Last-Modified"] = str(obj["LastModified"])
    return response


@ROUTER.get(
    "/v1/files/{file_path:path}",
    response_class=StreamingResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "File not found for the given `file_path`.",
        },
        status.HTTP_200_OK: {
            "description": "The file content.",
            "content": {
                "application/octet-stream": {
                    "schema": {"type": "string", "format": "binary"},
                },
            },
        },
    },
)
async def get_file(
    request: Request,
    file_path: str = Path(pattern=r"^([\w\d\s\-.]+/)*([\w\d\s\-.])+\.\w+$"),
) -> StreamingResponse:
    """Retrieve a file."""
    # 1 - Business logic: errors that the user can fix
    # error case: object does not exist in the bucket
    # error case: invalid inputs

    # 2 - errors that the user cannot fix
    # error case: not authenticated/authorized to make calls to AWS
    # error case: the bucket does not exist
    settings: Settings = request.app.state.settings

    object_exists = object_exists_in_s3(bucket_name=settings.s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")

    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name
    obj_response = fetch_s3_object(bucket_name=s3_bucket_name, object_key=file_path)
    return StreamingResponse(content=obj_response["Body"], media_type=obj_response["ContentType"])


@ROUTER.delete(
    "/v1/files/{file_path:path}",
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "File not found for given `file_path`."},
        status.HTTP_204_NO_CONTENT: {"description": "File successfully deleted at `file_path`."},
    },
)
async def delete_file(
    request: Request,
    file_path: str,
    response: Response,
) -> Response:
    """
    Delete a file.

    NOTE: DELETE requests MUST NOT return a body in the response.
    """
    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name

    object_exists = object_exists_in_s3(bucket_name=s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")

    delete_s3_object(bucket_name=s3_bucket_name, object_key=file_path)

    response.status_code = status.HTTP_204_NO_CONTENT
    return response
