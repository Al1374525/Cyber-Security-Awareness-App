import os
from openai import OpenAI

client = OpenAI(base_url="https://api.x.ai/v1", api_key=os.getenv("XAI_API_KEY"))
prompt = "Generate a simple JSON: {\"test\": \"value\"}"
try:
    response = client.chat.completions.create(
        model="grok-3-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=100
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {str(e)}")