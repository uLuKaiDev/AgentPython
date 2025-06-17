import os
import sys
from dotenv import load_dotenv # type: ignore
from google.genai import Client, types # type: ignore

from functions.get_file_content import get_file_content #type: ignore
from functions.get_files_info import get_files_info #type: ignore
from functions.run_python_file import run_python_file #type: ignore
from functions.write_file_content import write_file #type: ignore

from prompts import system_prompt
from call_function import available_functions


def get_api_key() -> str:
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set.")
        sys.exit(1)
    return api_key

def parse_arguments() -> tuple[str, bool]:
    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    if not args:
        print("Usage: python3 main.py <prompt>")
        sys.exit(1)
    return " ".join(args), verbose

def main():
    api_key = get_api_key()
    client = Client(api_key=api_key)

    user_prompt, verbose = parse_arguments()
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt,
        ),
    )


    if not response.text and not response.function_calls:
        print("Error: No response text or function calls received from the API.")
        sys.exit(1)

    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


    if response.function_calls:
        for call in response.function_calls:
            print(f"Calling function: {call.name}({call.args})")
            
            if call.name == "get_files_info":
                directory = call.args.get("directory", ".")
                result = get_files_info(working_directory=os.getcwd(), directory=directory)
                print(f"Function call result:\n {result}")
            elif call.name == "get_file_content":
                file_path = call.args.get("file_path")
                result = get_file_content(working_directory=os.getcwd(), file_path=file_path)
                print(f"Function call result:\n {result}")
            elif call.name == "run_python_file":
                file_path = call.args.get("file_path")
                result = run_python_file(working_directory=os.getcwd(), file_path=file_path)
                print(f"Function call result:\n {result}")
            elif call.name == "write_file_content":
                file_path = call.args.get("file_path")
                content = call.args.get("content")
                if content is None:
                    print("Error: 'content' argument is required for write_file_content.")
                    continue
                result = write_file(working_directory=os.getcwd(), file_path=file_path, content=content)
                print(f"Function call result:\n {result}")

            else:
                print(f"Error: Unknown function call {call.name}")
            
    # if response.text and not response.function_calls:
    #    print(f"Response text:\n{response.text}")

if __name__ == "__main__":
    main()