import os
import sys
from dotenv import load_dotenv # type: ignore
from google.genai import Client, types # type: ignore
from functions.get_files_info import get_files_info #type: ignore

GEMINI_MODEL = 'gemini-2.0-flash-001'
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan.

You can perform the following operations:
- List files and directories

All paths you provide should be relative to the working directory.
You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            )
        }
    )
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

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
        model=GEMINI_MODEL,
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
            else:
                print(f"Error: Unknown function call {call.name}")
            

    # print(response.text)

if __name__ == "__main__":
    main()