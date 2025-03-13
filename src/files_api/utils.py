"""Utilities file for files_api."""

from typing import List

from fastapi import status

# try:
# from files_api.s3.read_objects import object_exists_in_s3
# except ImportError as e:
#     print(f"ImportError in utils.py: {e}")
#     raise


def list_flatten(list_input: List[List]):
    """Flatten a list of lists into just one long list."""
    result = []

    for ls in list_input:
        for val in ls:
            result.append(val)

    return result


def object_exists_response(s3_bucket_name: str, file_path: str):
    """Check if object exists and return proper responses"""
    from files_api.s3.read_objects import object_exists_in_s3  # Is there no better way to avoid circular dependencies?

    print("object_exists_response called with parameters:", s3_bucket_name, file_path)
    object_already_exists = object_exists_in_s3(bucket_name=s3_bucket_name, object_key=file_path)
    print("Worked!")

    if object_already_exists:
        print("HERE 200!!!")
        response_message = f"Existing file updated at path: /{file_path}"
        status_code = status.HTTP_200_OK
    else:
        print("WHOMST 201---")
        response_message = f"New file uploaded at path: /{file_path}"
        status_code = status.HTTP_201_CREATED

    return (response_message, status_code)
