"""Define data model schemas."""

# read (cRud)
from datetime import datetime
from typing import (
    List,
    Optional,
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)
from typing_extensions import Self

# Default values are ok as long as they are overrideable by environment variables
DEFAULT_GET_FILES_PAGE_SIZE = 10
DEFAULT_GET_FILES_MIN_PAGE_SIZE = 10
DEFAULT_GET_FILES_MAX_PAGE_SIZE = 100
DEFAULT_GET_FILES_DIRECTORY = ""


class FileMetadata(BaseModel):
    """File metadata response details."""

    file_path: str = Field(description="Path to the file.")
    last_modified: datetime = Field(description="Date and time of last modification of file.")
    size_bytes: int = Field(description="Length of file in bytes.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "file_path": "path/to/pyproject.toml",
                "last_modified": "2022-01-01T00:00:00Z",
                "size_bytes": 512,
            }
        }
    )


class GetFilesQueryParams(BaseModel):
    """Fetch page of files request parameters with validation."""

    page_size: int = Field(
        DEFAULT_GET_FILES_PAGE_SIZE,
        ge=DEFAULT_GET_FILES_MIN_PAGE_SIZE,
        le=DEFAULT_GET_FILES_MAX_PAGE_SIZE,
        description="Number of files to return in each page. Mutually exclusive with `page_token`.",
    )
    directory: str = Field(
        default=DEFAULT_GET_FILES_DIRECTORY,
        description="Directory in which to list files. Mutually exclusive with `page_token`.",
    )
    page_token: Optional[str] = Field(
        default=None, description="Token to continue pagination. Mutually exclusive with `directory` and `page_size`."
    )

    @model_validator(mode="after")
    def check_page_token_exclusivity(self) -> Self:
        """Validate that the page_token parameter does not coexist with directory and page_size."""
        if self.page_token:
            get_files_query_params: dict = self.model_dump(exclude_unset=True)
            page_size_set = "page_size" in get_files_query_params.keys()
            directory_set = "directory" in get_files_query_params.keys()
            if page_size_set or directory_set:
                raise ValueError("page_token is mutually exclusive with page_size and directory")
        return self


class GetFilesResponse(BaseModel):
    """Fetch page of files response data."""

    files: List[FileMetadata] = Field(description="List of file metadata.")
    next_page_token: Optional[str] = Field(
        description="Next page token. Missing if the response contained the last page."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "files": [
                    {
                        "file_path": "path/to/pyproject.toml",
                        "last_modified": "2022-01-01T00:00:00Z",
                        "size_bytes": 512,
                    },
                    {
                        "file_path": "path/to/Makefile",
                        "last_modified": "2022-01-01T00:00:00Z",
                        "size_bytes": 256,
                    },
                ],
                "next_page_token": "next_page_token_example",
            }
        }
    )


class PutFileResponse(BaseModel):
    """Fetch create file response data."""

    file_path: str = Field(description="Path to the created or updated file.")
    message: str = Field(description="Additional details on the creation or update of the file.")


PUT_FILE_EXAMPLES = {
    "200": {
        "content": {
            "application/json": {
                "example": {"file_path": "path/to/existing_file.txt", "message": "File successfully updated."}
            }
        }
    },
    "201": {
        "content": {
            "application/json": {
                "example": {"file_path": "path/to/new_file.txt", "message": "New file uploaded successfully."}
            }
        }
    },
}
