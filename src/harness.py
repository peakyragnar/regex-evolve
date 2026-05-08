import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def generate_candidates(prompt: str, n: int) -> list[str]:
    instruction = (
        f"\n\nReturn exactly {n} regex patterns, one per line. "
        "No commentary. No markdown. No numbering. Just the patterns."
    )
    response = call_gemini_with_retry(prompt + instruction)
    lines = response.text.split("\n")
    patterns = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            patterns.append(stripped)
    return patterns


def call_gemini_with_retry(content, max_retries=3, sleep_seconds=60):
    for attempt in range(max_retries + 1):
        try:
            return client.models.generate_content(
                model="gemini-2.5-flash-lite",
                contents=content,
            )
        except errors.ClientError as e:
            if "RESOURCE_EXHAUSTED" not in str(e) or attempt == max_retries:
                raise
            print(f"  Rate limited. Sleeping {sleep_seconds}s "
                  f"(retry {attempt + 1}/{max_retries})...")
            time.sleep(sleep_seconds)
    raise RuntimeError("unreachable")


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
