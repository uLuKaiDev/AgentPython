import os
import sys
from dotenv import load_dotenv
from google.genai import Client, types

GEMINI_MODEL = 'gemini-2.0-flash-001'

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
    )

    if not response.text:
        print("Error: No response text received from the API.")
        sys.exit(1)

    if verbose:
        print(f"User prompt: {user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    print(response.text)

if __name__ == "__main__":
    main()