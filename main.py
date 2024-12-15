import os
import asyncio
import logging
import re
from google import genai
from google.genai import types

class GeminiClient:
    """
    Encapsulates the Gemini API client and its related functionality.
    This class handles the connection to the Gemini API, sending prompts,
    handling responses, and writing generated code to a file.
    """
    def __init__(self, api_key=None, model_name="gemini-2.0-flash-exp"):
        """
        Initializes the GeminiClient.

        Args:
            api_key (str, optional): The Gemini API key. Defaults to None, in this case the client
            will try to load it from the env variables
            model_name (str, optional): The name of the Gemini model to use.
                Defaults to "gemini-2.0-flash-exp".
        """
        # If the api key is not given, try to load from env variables
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        # If the api key is not given anywhere, raise error.
        if not self.api_key:
          raise ValueError("No GEMINI_API_KEY provided in env variables or constructor.")

        # Set model name
        self.model_name = model_name

        # Initialize the Gemini client.
        self.client = genai.Client(
            api_key=self.api_key,
            http_options={'api_version': 'v1alpha'}
        )

        # Set up the logger for this class.
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.INFO)  # Set to 'DEBUG' for more info


    async def run_query(self, prompt, modality='TEXT', tools=None):
        """
        Runs a query against the Gemini model.

        Args:
            prompt (str): The prompt to send to the model.
            modality (str, optional): The desired response modality.
                Defaults to 'TEXT'.
            tools (list, optional): A list of tools to use with the model.
                Defaults to None.
        """
        # If no tools are given, initialize an empty list
        if tools is None:
            tools = []

        # Create a configuration for the model.
        config = {
            "tools": tools,
            "generation_config": {
                "response_modalities": [modality]
            }
        }

        # Connect to the Gemini live session.
        async with self.client.aio.live.connect(model=self.model_name, config=config) as session:
            print(prompt)
            print('-------------------------------')
            await session.send(prompt, end_of_turn=True)

            # Initialize response text and code
            full_response_text = ""
            python_code = ""

            # Process responses from the model.
            async for response in session.receive():
                self.logger.debug(str(response))
                server_content = response.server_content
                # Handle the response
                if server_content:
                    text, code = self._handle_server_content(server_content)
                    full_response_text += text
                    if code:
                       python_code = code

                # Handle tool calls.
                tool_call = response.tool_call
                if tool_call:
                   await self._handle_tool_call(session, tool_call)

            # Write generated code to a file.
            self._write_python_to_file(python_code, "graph.py")

    def _handle_server_content(self, server_content):
        """
        Processes the server content received from the Gemini API.

        Args:
            server_content (google.generativeai.types.ServerContent):
                The server content to process.

        Returns:
            tuple: A tuple containing the full text response and any extracted code.
        """
        full_text = ""
        code = ""
        # Handle model turn
        model_turn = server_content.model_turn
        if model_turn:
            for part in model_turn.parts:
                text = part.text
                if text:
                    print(text)
                    full_text += text

                executable_code = part.executable_code
                if executable_code:
                    print('-------------------------------')
                    print(f'``` python\n{executable_code.code}\n```')
                    print('-------------------------------')
                    code = executable_code.code  # Extract only the code block

                code_execution_result = part.code_execution_result
                if code_execution_result:
                    print('-------------------------------')
                    print(f'```\n{code_execution_result.output}\n```')
                    print('-------------------------------')
                    full_text += f'\n```\n{code_execution_result.output}\n```\n'

        # Handle grounding metadata
        grounding_metadata = getattr(server_content, 'grounding_metadata', None)
        if grounding_metadata:
            print(grounding_metadata.search_entry_point.rendered_content)
            full_text += f"\n{grounding_metadata.search_entry_point.rendered_content}\n"
        return full_text, code

    async def _handle_tool_call(self, session, tool_call):
        """
        Handles tool calls received from the Gemini API.

        Args:
            session (google.generativeai.live.LiveSession): The Gemini session.
            tool_call (google.generativeai.types.ToolCall): The tool call to handle.
        """
        # Iterate over each function call.
        for fc in tool_call.function_calls:
            # Create the tool response
            tool_response = types.LiveClientToolResponse(
                function_responses=[types.FunctionResponse(
                    name=fc.name,
                    id=fc.id,
                    response={'result': 'ok'},
                )]
            )
            print('>>> ', tool_response)
            # Send the tool response back to the session
            await session.send(tool_response)


    def _write_python_to_file(self, code, filename):
        """
        Writes Python code to a file.

        Args:
            code (str): The Python code to write.
            filename (str): The name of the file to write to.
        """
        if code:
            with open(filename, 'w') as f:
                f.write(code)
            print(f"Python code written to {filename}")
        else:
            print("No Python code to write.")

class PromptBuilder:
    """
    Responsible for constructing the prompt for the Gemini model.
    This class helps in creating a specific prompt based on the user input.
    """
    def __init__(self, user_prompt):
       """
        Initializes the PromptBuilder.

        Args:
            user_prompt (str): The user's input/topic.
        """
       self.user_prompt = user_prompt

    def build_prompt(self):
        """
        Builds the prompt for the Gemini model.

        Returns:
            str: The constructed prompt.
        """
        return f"""
        I want you to:
        1. Search for relevant information regarding the topic the user will specify
        2. Then, based on the information found, create a matplotlib graph in python.
        
        Here is the user topic: {self.user_prompt}
        """

class ToolConfig:
    """
    Manages the configuration of tools used with the Gemini model.
    This class specifies which tools the model will use during its execution.
    """
    def get_tools(self):
        """
        Returns the configured tools.

        Returns:
            list: A list of tool configurations.
        """
        return [
            {'google_search': {}},
            {'code_execution': {}}
        ]

async def main():
    """
    Main function to execute the program.
    This function gets the user input, builds the prompt, sets up the tools,
    and then runs the query using Gemini client.
    """
    user_prompt = input("Please enter a topic for which you'd like a graph to be generated: ")

    # Instantiate the helper classes
    prompt_builder = PromptBuilder(user_prompt)
    tool_config = ToolConfig()
    gemini_client = GeminiClient()


    # Build prompt and tools
    prompt = prompt_builder.build_prompt()
    tools = tool_config.get_tools()

    # Run the query
    await gemini_client.run_query(prompt, tools=tools, modality="TEXT")


if __name__ == '__main__':
    asyncio.run(main())