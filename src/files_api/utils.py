
from typing import List


def list_flatten(list_input: List[List]):
    result = []

    for ls in list_input:
        for val in ls:
            result.append(val)
    
    return result