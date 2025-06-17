import os
from google.genai import types  # type: ignore

MAX_CHARS = 10000

# Returns the file content as a string or as an error string if something goes wrong.
def get_file_content(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(abs_file_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        with open(abs_file_path, 'r', encoding='utf-8') as file:
            content = file.read(MAX_CHARS)
            if len(content) == MAX_CHARS:
                content += (
                    f'[...File "{file_path}" truncated at {MAX_CHARS} characters...]\n'
                )
        return content
    except Exception as e:
        return f'Error: reading file "{file_path}": {e}'

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Retrieves the content of a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to retrieve, relative to the working directory.",
            )
        }
    )
)
