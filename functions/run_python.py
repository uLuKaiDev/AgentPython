import os
import subprocess

def run_python_file(working_directory, file_path):
    abs_working_dir = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not abs_file_path.startswith(abs_working_dir):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    if not os.path.isfile(abs_file_path):
        return f'Error: File "{file_path}" not found.'
    
    if not abs_file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        result = subprocess.run(
            ['python3', abs_file_path],
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=abs_working_dir
        )

        stdout = result.stdout.strip() if result.stdout else "No output produced."
        stderr = result.stderr.strip() if result.stderr else ""

        if stderr:
            return f"STDOUT:\n{stdout}\nSTDERR:\n{stderr}\nProcess exited with code {result.returncode}"
        else:
            return f"STDOUT:\n{stdout}"

    except subprocess.TimeoutExpired:
        return f"Error: File execution timed out after 30 seconds."
    except subprocess.CalledProcessError as e:
        # This is for when the Python script exits with a non-zero code
        return f"STDOUT:\n{e.stdout.strip()}\nSTDERR:\n{e.stderr.strip()}\nProcess exited with code {e.returncode}"
    except Exception as e:
        return f"Error: executing Python file: {e}"
