import openai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()
api_key = "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"

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in .env file")

print("API Key Loaded Successfully:", api_key[:5] + "****")

def analyze_resume(resume_text):
    if not resume_text:
        return ["Error: Resume content is empty."]

    prompt = f"""
    You are an AI HR assistant. Analyze the following resume and generate 20 relevant interview questions:

    {resume_text}

    Provide the questions as a numbered list.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an AI HR assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        if response["choices"]:
            questions = response["choices"][0]["message"]["content"].strip().split("\n")
            return [q.strip() for q in questions if q.strip()]

        return ["Error: No response from OpenAI."]
    except openai.error.OpenAIError as e:
        return [f"OpenAI API Error: {str(e)}"]
    except Exception as e:
        return [f"Unexpected Error: {str(e)}"]

# Sinov qilish
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Your prompt here"}]
)
print(response["choices"][0]["message"]["content"])
