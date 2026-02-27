from openai import OpenAI

client = OpenAI(api_key="הדבק_כאן_את_ה_key_שלך")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "תגיד שלום"}],
)

print(response.choices[0].message.content)
