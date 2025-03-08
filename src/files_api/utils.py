"""Utilities file for files_api."""

from typing import List


def list_flatten(list_input: List[List]):
    """Flatten a list of lists into just one long list."""
    result = []

    for ls in list_input:
        for val in ls:
            result.append(val)

    return result
