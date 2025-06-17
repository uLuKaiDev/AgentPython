import os

from google.genai import types  # type: ignore

def write_file(working_directory, file_path, content):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    # If file_path doesn't exist, create it 
    if not os.path.exists(os.path.dirname(abs_file_path)):
        try:
            os.makedirs(os.path.dirname(abs_file_path))
        except Exception as e:
            return f'Error: creating directory for "{file_path}": {e}'

    if os.path.exists(abs_file_path) and os.path.isdir(abs_file_path):
        return f'Error: "{file_path}" is a directory, not a file'

    try:
        with open(abs_file_path, 'w', encoding='utf-8') as file:
            file.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: writing file "{file_path}": {e}'
    
schema_write_file_content = types.FunctionDeclaration(
    name="write_file_content",
    description="Writes content to a file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            )
        }
    )
)
