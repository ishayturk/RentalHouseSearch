from openai import OpenAI

client = OpenAI(api_key="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")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "תגיד שלום"}],
)

print(response.choices[0].message.content)
