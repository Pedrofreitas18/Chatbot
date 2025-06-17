# nlp/extractor.py
import requests
import json
import re
from ..models import get_last_messages

def extract_structured_data(user_message: str, fields: list[str], context: str, user_number: str) -> dict:
    prompt = f"""
Context: {context}

History: 
\"\"\"{get_last_messages(user_number, limit=5)}\"\"\"

User Message:
\"\"\"{user_message}\"\"\"

Extract the following fields in JSON format:
{', '.join(fields)}

If not able of recover any field, return it's value as blank

Return only the JSON.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "openchat", "prompt": prompt, "stream": False}
    )

    result = response.json()["response"]

    try:
        json_str = re.search(r'\{.*\}', result, re.DOTALL).group()
        return json.loads(json_str)
    except:
        return {}