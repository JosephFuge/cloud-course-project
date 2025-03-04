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
    FileMetadata,
    GetFilesQueryParams,
    GetFilesResponse,
    PutFileResponse,
)
from files_api.settings import Settings

ROUTER = APIRouter()

##################
# --- Routes --- #
##################


@ROUTER.put("/files/{file_path:path}")
async def upload_file(request: Request, file_path: str, file: UploadFile, response: Response) -> PutFileResponse:
    """Upload a file."""

    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name

    file_contents: bytes = await file.read()

    object_already_exists = object_exists_in_s3(bucket_name=s3_bucket_name, object_key=file_path)

    if object_already_exists:
        response_message = f"Existing file updated at path: /{file_path}"
        response.status_code = status.HTTP_200_OK
    else:
        response_message = f"New file uploaded at path: /{file_path}"
        response.status_code = status.HTTP_201_CREATED

    upload_s3_object(
        bucket_name=s3_bucket_name, object_key=file_path, file_content=file_contents, content_type=file.content_type
    )

    return PutFileResponse(file_path=file_path, message=response_message)


@ROUTER.get("/files")
async def list_files(
    request: Request,
    query_params: GetFilesQueryParams = Depends(),
):
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


@ROUTER.head("/files/{file_path:path}")
async def get_file_metadata(request: Request, file_path: str, response: Response) -> Response:
    """Retrieve file metadata.

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


@ROUTER.get("/files/{file_path:path}")
async def get_file(
    request: Request,
    file_path: str = Path(pattern=r"^([\w\d\s\-.]+/)*([\w\d\s\-.])+\.\w+$"),
):
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


@ROUTER.delete("/files/{file_path:path}")
async def delete_file(
    request: Request,
    file_path: str,
    response: Response,
) -> Response:
    """Delete a file.

    NOTE: DELETE requests MUST NOT return a body in the response."""
    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name

    object_exists = object_exists_in_s3(bucket_name=s3_bucket_name, object_key=file_path)
    if not object_exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {file_path}")

    delete_s3_object(bucket_name=s3_bucket_name, object_key=file_path)

    response.status_code = status.HTTP_204_NO_CONTENT
    return response
