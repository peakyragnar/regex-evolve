import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_candidates(prompt: str, n: int) -> list[str]:
    instruction = (
        f"\n\nReturn exactly {n} regex patterns, one per line. "
        "No commentary. No markdown. No numbering. Just the patterns."
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt + instruction,
    )
    lines = response.text.split("\n")
    patterns = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            patterns.append(stripped)
    return patterns


if __name__ == "__main__":
    prompt = (
        "Find a Python regex pattern that matches exactly the strings "
        "'cat', 'dog', and 'bird' (full match, anchored), "
        "and rejects all other strings."
    )
    candidates = generate_candidates(prompt, n=5)
    print(f"Got {len(candidates)} candidates:")
    for i, candidate in enumerate(candidates, start=1):
        print(f"  {i}. {candidate}")
