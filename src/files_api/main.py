from datetime import datetime
from typing import (
    List,
    Optional,
)

from fastapi import (
    Depends,
    FastAPI,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from files_api.s3.write_objects import upload_s3_object

#####################
# --- Constants --- #
#####################

S3_BUCKET_NAME = "some-bucket"

APP = FastAPI()

####################################
# --- Request/response schemas --- #
####################################


# read (cRud)
class FileMetadata(BaseModel):
    file_path: str
    last_modified: datetime
    size_bytes: int

class GetFilesQueryParams(BaseModel):
    page_size: int = 10
    directory: Optional[str] = ""
    page_token: Optional[str] = None

class GetFilesResponse(BaseModel):
    files: List[FileMetadata]
    next_page_token: Optional[str]

# more pydantic models ...

class PutFileResponse(BaseModel):
    file_path: str
    message: str


##################
# --- Routes --- #
##################


@APP.put("/files/{file_path:path}")
async def upload_file(file_path: str, file: UploadFile, response: Response) -> PutFileResponse:
    """Upload a file."""

    file_contents: bytes = await file.read()

    object_already_exists = object_exists_in_s3(bucket_name=S3_BUCKET_NAME, object_key=file_path)
    
    if object_already_exists:
        response_message = f"Existing file updated at path: /{file_path}"
        response.status_code = status.HTTP_200_OK
    else:
        response_message = f"New file uploaded at path: /{file_path}"
        response.status_code = status.HTTP_201_CREATED

    upload_s3_object(
        bucket_name=S3_BUCKET_NAME,
        object_key=file_path,
        file_content=file_contents,
        content_type=file.content_type
    )

    return PutFileResponse(
        file_path=file_path,
        message=response_message
    )


@APP.get("/files")
async def list_files(
    query_params: GetFilesQueryParams = Depends(),
):
    """List files with pagination."""

    if query_params.page_token:
        obj_page = fetch_s3_objects_using_page_token(
            bucket_name=S3_BUCKET_NAME,
            continuation_token=query_params.page_token,
            max_keys=query_params.page_size
        )
    elif query_params.directory:
        obj_page = fetch_s3_objects_metadata(
            bucket_name=S3_BUCKET_NAME,
            prefix=query_params.directory,
            max_keys=query_params.page_size
        )
    else:
        obj_page = fetch_s3_objects_metadata(
            bucket_name=S3_BUCKET_NAME,
            max_keys=query_params.page_size
        )
    
    return GetFilesResponse(
        files=[FileMetadata(
            file_path=file["Key"],
            last_modified=file["LastModified"],
            size_bytes=file["Size"]
        ) for file in obj_page[0]],
        next_page_token=obj_page[1]
    )


@APP.head("/files/{file_path:path}")
async def get_file_metadata(file_path: str, response: Response) -> Response:
    """Retrieve file metadata.

    Note: by convention, HEAD requests MUST NOT return a body in the response.
    """

    obj = fetch_s3_object(
        bucket_name=S3_BUCKET_NAME,
        object_key=file_path
    )

    response.status_code = status.HTTP_200_OK
    response.headers["Content-Type"] = obj["ContentType"]
    response.headers["Content-Length"] = str(obj["ContentLength"])
    response.headers["Last-Modified"] = str(obj["LastModified"])
    return response

@APP.get("/files/{file_path:path}")
async def get_file(
    file_path: str,
):
    """Retrieve a file."""
    
    obj_response = fetch_s3_object(bucket_name=S3_BUCKET_NAME, object_key=file_path)
    return StreamingResponse(
        content=obj_response["Body"],
        media_type=obj_response["ContentType"]
    )


@APP.delete("/files/{file_path:path}")
async def delete_file(
    file_path: str,
    response: Response,
) -> Response:
    """Delete a file.

    NOTE: DELETE requests MUST NOT return a body in the response."""
    delete_s3_object(bucket_name=S3_BUCKET_NAME, object_key=file_path)

    response.status_code = status.HTTP_204_NO_CONTENT
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(APP, host="0.0.0.0", port=8000)
