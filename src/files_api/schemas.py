"""Define data model schemas."""

# read (cRud)
from datetime import datetime
from typing import (
    List,
    Optional,
    Self,
)

from pydantic import (
    BaseModel,
    Field,
    model_validator,
)

# Default values are ok as long as they are overrideable by environment variables
DEFAULT_GET_FILES_PAGE_SIZE = 10
DEFAULT_GET_FILES_MIN_PAGE_SIZE = 10
DEFAULT_GET_FILES_MAX_PAGE_SIZE = 100
DEFAULT_GET_FILES_DIRECTORY = ""


class FileMetadata(BaseModel):
    """File metadata response details."""

    file_path: str
    last_modified: datetime
    size_bytes: int


# more pydantic models ...


class GetFilesQueryParams(BaseModel):
    """Fetch page of files request parameters with validation."""

    page_size: int = Field(
        DEFAULT_GET_FILES_PAGE_SIZE,
        ge=DEFAULT_GET_FILES_MIN_PAGE_SIZE,
        le=DEFAULT_GET_FILES_MAX_PAGE_SIZE,
    )
    directory: str = DEFAULT_GET_FILES_DIRECTORY
    page_token: Optional[str] = None

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

    files: List[FileMetadata]
    next_page_token: Optional[str]


class PutFileResponse(BaseModel):
    """Fetch create file response data."""

    file_path: str
    message: str
