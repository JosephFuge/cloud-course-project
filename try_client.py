import time
from pprint import pprint

import files_api_sdk
from files_api_sdk.rest import ApiException

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = files_api_sdk.Configuration(
    host = "http://localhost:8000"
)



# Enter a context with an instance of the API client
with files_api_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = files_api_sdk.FilesApi(api_client)
    file_path = 'file_path_example2.txt' # str | 
    file = "./pyproject.toml"

    try:
        # Delete File
        api_response = api_instance.upload_file_v1_files_file_path_put(file_path, file)
        print("The response of DefaultApi->upload_file_v1_files_file_path_put:\n")
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling DefaultApi->upload_file_v1_files_file_path_put: %s\n" % e)
