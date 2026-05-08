from harness import generate_candidates
from verifier import score
from best_of_n import build_prompt


def iterative_refinement(description, test_cases, examples, n_per_round, n_rounds, top_k):
    history = []
    best_per_round = []

    for round_num in range(1, n_rounds + 1):
        if round_num == 1:
            prompt = build_prompt(description, examples)
        else:
            top_so_far = top_k_unique(history, top_k)
            prompt = build_iterative_prompt(description, examples, top_so_far)

        print(f"\n{'=' * 70}")
        print(f"ROUND {round_num} — prompt sent to Gemini:")
        print(f"{'=' * 70}")
        print(prompt)
        print(f"{'=' * 70}\n")

        candidates = generate_candidates(prompt, n_per_round)
        round_scored = []
        for candidate in candidates:
            s = score(candidate, test_cases)
            round_scored.append((s, candidate))
        round_scored.sort(reverse=True)
        history.extend(round_scored)

        print(f"Round {round_num} candidates ({len(round_scored)} returned):")
        for s, candidate in round_scored:
            print(f"  {s:7.3f}  {candidate}")

        best_score, best_regex = max(history)
        best_per_round.append((round_num, best_score, best_regex))
        print(f"\nRound {round_num} best ever: {best_score:.3f}  {best_regex!r}")

    return history, best_per_round


def build_iterative_prompt(description, examples, top_candidates):
    lines = [description, "", "Examples:"]
    for input_string, expected in examples:
        verdict = "MATCH" if expected else "NO MATCH"
        lines.append(f"  {input_string!r:12}  ->  {verdict}")

    lines.append("")
    lines.append("Previous attempts and their scores (higher is better):")
    for s, candidate in top_candidates:
        lines.append(f"  {s:7.3f}  {candidate}")

    lines.append("")
    lines.append(
        "These patterns have been tried already. Generate NEW patterns "
        "that try to beat the top score. Look for shorter or simpler "
        "approaches that still classify all examples correctly."
    )
    return "\n".join(lines)


def top_k_unique(history, k):
    seen = set()
    result = []
    for entry in sorted(history, reverse=True):
        score_val, regex = entry
        if regex not in seen:
            seen.add(regex)
            result.append(entry)
            if len(result) == k:
                break
    return result


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

    history, best_per_round = iterative_refinement(
        description=description,
        test_cases=cases,
        examples=examples,
        n_per_round=10,
        n_rounds=5,
        top_k=5,
    )

    print(f"\n{'=' * 70}")
    print("CONVERGENCE — best score after each round")
    print(f"{'=' * 70}")
    for round_num, score_val, regex in best_per_round:
        print(f"Round {round_num}: {score_val:7.3f}  {regex!r}")

    final_score, final_regex = max(history)
    print(f"\nFinal winner: {final_regex!r}  (score {final_score:.3f})")
