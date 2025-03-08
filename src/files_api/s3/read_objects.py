"""Functions for reading objects from an S3 bucket--the "R" in CRUD."""

from typing import (
    Any,
    Dict,
    Optional,
)

import boto3
import botocore

from files_api.utils import list_flatten

try:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import (
        GetObjectOutputTypeDef,
        ObjectTypeDef,
    )
except ImportError:
    ...

DEFAULT_MAX_KEYS = 1_000


def object_exists_in_s3(bucket_name: str, object_key: str, s3_client: Optional["S3Client"] = None) -> bool:
    """
    Check if an object exists in the S3 bucket using head_object.

    :param bucket_name: Name of the S3 bucket.
    :param object_key: Key of the object to check.
    :param s3_client: Optional S3 client to use. If not provided, a new client will be created.

    :return: True if the object exists, False otherwise.
    """

    try:
        s3_client = s3_client or boto3.client("s3")
        obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        obj.get("Body")
    except botocore.exceptions.ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404" or error_code == "NoSuchKey":
            return False

    return True


def fetch_s3_object(
    bucket_name: str,
    object_key: str,
    s3_client: Optional["S3Client"] = None,
) -> "GetObjectOutputTypeDef":
    """
    Fetch metadata of an object in the S3 bucket.

    :param bucket_name: Name of the S3 bucket.
    :param object_key: Key of the object to fetch.
    :param s3_client: Optional S3 client to use. If not provided, a new client will be created.

    :return: Metadata of the object.
    """
    s3_client = s3_client or boto3.client("s3")
    obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    return obj


def fetch_s3_objects_using_page_token(
    bucket_name: str,
    continuation_token: str,
    max_keys: int | None = None,
    s3_client: Optional["S3Client"] = None,
) -> tuple[list["ObjectTypeDef"], Optional[str]]:
    """
    Fetch list of object keys and their metadata using a continuation token.

    :param bucket_name: Name of the S3 bucket to list objects from.
    :param continuation_token: Token for fetching the next page of results where the last page left off.
    :param max_keys: Maximum number of keys to return within this page.
    :param s3_client: Optional S3 client to use. If not provided, a new client will be created.

    :return: Tuple of a list of objects and the next continuation token.
        1. Possibly empty list of objects in the current page.
        2. Next continuation token if there are more pages, otherwise None.
    """
    s3_client = s3_client or boto3.client("s3")
    max_keys = max_keys or DEFAULT_MAX_KEYS
    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(
        Bucket=bucket_name, PaginationConfig={"MaxItems": max_keys, "StartingToken": continuation_token}
    )

    object_data = list(list_flatten([page["Contents"] for page in page_iterator]))

    return (object_data, str(page_iterator.resume_token))


def fetch_s3_objects_metadata(
    bucket_name: str,
    prefix: Optional[str] = None,
    max_keys: Optional[int] = DEFAULT_MAX_KEYS,
    s3_client: Optional["S3Client"] = None,
) -> tuple[list["ObjectTypeDef"], Optional[str]]:
    """
    Fetch list of object keys and their metadata.

    :param bucket_name: Name of the S3 bucket to list objects from.
    :param prefix: Prefix to filter objects by.
    :param max_keys: Maximum number of keys to return within this page.
    :param s3_client: Optional S3 client to use. If not provided, a new client will be created.

    :return: Tuple of a list of objects and the next continuation token.
        1. Possibly empty list of objects in the current page.
        2. Next continuation token if there are more pages, otherwise None.
    """

    s3_client = s3_client or boto3.client("s3")
    max_keys = max_keys or DEFAULT_MAX_KEYS
    params: Dict[str, Any] = {}
    if prefix is not None:
        params["Prefix"] = prefix

    objects_metadata = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=max_keys, **params)

    return (
        objects_metadata["Contents"],
        objects_metadata["NextContinuationToken"] if objects_metadata["IsTruncated"] else None,
    )
