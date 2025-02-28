from openai import OpenAI

api_key = "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"

client = OpenAI(api_key=api_key)

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert hr specialist. Your job is to ask one question related to Programming"},
        {
            "role": "user",
            "content": "ask question in short form depending on this resume {extracted_text}."
        }
    ]
)

print(completion.choices[0].message.content)