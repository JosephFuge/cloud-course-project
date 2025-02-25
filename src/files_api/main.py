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


# more pydantic models ...


##################
# --- Routes --- #
##################


@APP.put("/files/{file_path:path}")
async def upload_file(file_path: str, file: UploadFile, response: Response):
    """Upload a file."""
    ...


@APP.get("/files")
async def list_files(
    query_params=...,
):
    """List files with pagination."""
    ...


@APP.head("/files/{file_path:path}")
async def get_file_metadata(file_path: str, response: Response) -> Response:
    """Retrieve file metadata.

    Note: by convention, HEAD requests MUST NOT return a body in the response.
    """
    return


@APP.get("/files/{file_path:path}")
async def get_file(
    file_path: str,
):
    """Retrieve a file."""
    ...


@APP.delete("/files/{file_path:path}")
async def delete_file(
    file_path: str,
    response: Response,
) -> Response:
    """Delete a file.

    NOTE: DELETE requests MUST NOT return a body in the response."""
    return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(APP, host="0.0.0.0", port=8000)
