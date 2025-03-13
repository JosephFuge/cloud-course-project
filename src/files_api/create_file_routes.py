"""Define API routes."""

from fastapi import (
    APIRouter,
    Request,
    Response,
    status,
)

from files_api.genai.create_text import create_text_file
from files_api.s3.write_objects import upload_s3_object
from files_api.schemas import (
    PUT_FILE_EXAMPLES,
    PutFileResponse,
)
from files_api.settings import Settings
from files_api.utils import object_exists_response

ROUTER = APIRouter(tags=["Create Files"])

##################
# --- Routes --- #
##################


@ROUTER.put(
    "/v1/files/{file_type:str}/{file_path:path}",
    responses={status.HTTP_200_OK: {"model": PutFileResponse, **PUT_FILE_EXAMPLES['200']},
        status.HTTP_201_CREATED: {"model": PutFileResponse, **PUT_FILE_EXAMPLES['201']},},
)
async def create_file(request: Request, file_path: str, file_type: str, prompt: str, response: Response) -> PutFileResponse:
    """Create a file."""
    settings = request.app.state.settings
    s3_bucket_name = settings.s3_bucket_name

    response_message, response.status_code = object_exists_response(s3_bucket_name, file_path)

    if file_type == "text":
        file_contents: bytes = create_text_file(prompt, settings.openai_api_key)
        content_type = "text/plain"
    elif file_type == "image":
        file_contents = create_text_file(prompt, settings.openai_api_key)
        content_type = "image/png"
    elif file_type == "audio":
        file_contents = create_text_file(prompt, settings.openai_api_key)
        content_type = "audio/mpeg"

    upload_s3_object(
        bucket_name=s3_bucket_name, object_key=file_path, file_content=file_contents, content_type=content_type
    )

    return PutFileResponse(file_path=file_path, message=response_message)