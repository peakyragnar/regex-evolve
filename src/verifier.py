import re

LENGTH_PENALTY = 0.01


def score(regex_string: str, test_cases: list[tuple[str, bool]]) -> float:
    try:
        pattern = re.compile(regex_string)
    except re.error:
        return 0.0
    correct = 0
    for input_string, expected in test_cases:
        matched = pattern.fullmatch(input_string) is not None
        if matched == expected:
            correct += 1
    return correct - LENGTH_PENALTY * len(regex_string)


if __name__ == "__main__":
    from problems.cat_dog_bird import cases, description

    candidates = [
        "cat|dog|bird",
        "(cat|dog|bird)",
        "(?:cat|dog|bird)",
        "c(at)|d(og)|b(ird)",
        "^(cat|dog|bird)$",
        "[invalid(",
        ".*",
    ]

    print(f"Problem: {description}")
    print(f"Test cases: {len(cases)}\n")
    print(f"  {'score':>7}  pattern")
    print(f"  {'-----':>7}  -------")
    for candidate in candidates:
        s = score(candidate, cases)
        print(f"  {s:7.3f}  {candidate}")
