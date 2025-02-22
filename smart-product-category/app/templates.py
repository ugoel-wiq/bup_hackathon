
JSON_RESPONSE_TEMPLATE = """You are a helpful AI assistant that always responds in valid JSON format.

Your task is to respond to the following prompt and structure your response according to the exact JSON schema provided.

Prompt: {prompt}

You must format your entire response as a valid JSON object following this exact schema:
{json_structure}

Important:
1. Ensure your response is valid JSON
2. Start with a {{ (opening curly brace)
3. End with a }} (closing curly brace)
4. Use double quotes for strings
5. Follow the schema exactly

Response:"""