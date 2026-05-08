from harness import generate_candidates
from verifier import score


def best_of_n(description, test_cases, examples, n):
    prompt = build_prompt(description, examples)
    candidates = generate_candidates(prompt, n)
    scored = []
    for candidate in candidates:
        s = score(candidate, test_cases)
        scored.append((s, candidate))
    scored.sort(reverse=True)
    best_score, best_regex = scored[0]
    return best_regex, best_score, scored


def build_prompt(description, examples):
    lines = [description, "", "Examples:"]
    for input_string, expected in examples:
        verdict = "MATCH" if expected else "NO MATCH"
        lines.append(f"  {input_string!r:12}  ->  {verdict}")
    lines.append("")
    lines.append(
        "Generate genuinely different approaches. Vary structure, "
        "specificity, and style across patterns. Avoid repeating "
        "the same regex with only cosmetic changes."
    )
    return "\n".join(lines)


if __name__ == "__main__":
    from problems.cat_dog_bird import cases, description

    examples = [
        ("cat", True),
        ("dog", True),
        ("bird", True),
        ("fish", False),
        ("category", False),
        ("CAT", False),
    ]

    print("Prompt sent to Gemini:")
    print("-" * 60)
    print(build_prompt(description, examples))
    print("-" * 60)
    print()

    best_regex, best_score, all_scored = best_of_n(
        description=description,
        test_cases=cases,
        examples=examples,
        n=20,
    )

    print(f"Asked Gemini for 20 candidates.")
    print(f"Got {len(all_scored)} parseable candidates back.\n")
    print("All candidates, sorted best to worst:")
    for s, candidate in all_scored:
        print(f"  {s:7.3f}  {candidate}")
    print()
    print(f"Winner: {best_regex!r}  (score {best_score:.3f})")
