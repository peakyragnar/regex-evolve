import random
from harness import generate_candidates
from verifier import score
from best_of_n import best_of_n


def evolutionary_search(description, test_cases, examples,
                        pop_size, n_generations,
                        parents_per_gen, offspring_per_parent):
    print("=" * 70)
    print("SEEDING POPULATION (running Best-of-N)")
    print("=" * 70)
    population = seed_population(
        description, test_cases, examples, target_size=pop_size
    )

    print(f"\nInitial population ({len(population)} candidates):")
    for s, candidate in population:
        print(f"  {s:7.3f}  {candidate}")

    history = [(0, list(population))]

    for gen in range(1, n_generations + 1):
        print(f"\n{'=' * 70}")
        print(f"GENERATION {gen}")
        print(f"{'=' * 70}")

        offspring = run_one_generation(
            population, description, examples, test_cases,
            parents_per_gen, offspring_per_parent,
        )
        population = next_population(population, offspring, pop_size)
        history.append((gen, list(population)))

        gen_best_score, gen_best_regex = max(population)
        print(f"\nGeneration {gen} best: {gen_best_score:.3f}  {gen_best_regex!r}")
        print(f"Generation {gen} population size: {len(population)}")

    return history


def run_one_generation(population, description, examples, test_cases,
                        parents_per_gen, offspring_per_parent):
    offspring = []
    for parent_num in range(1, parents_per_gen + 1):
        parent = sample_parent(population)
        parent_score, parent_regex = parent
        print(f"\nParent {parent_num}: score {parent_score:.3f}  {parent_regex!r}")

        children = mutate(parent, description, examples, n=offspring_per_parent)
        print("  Offspring:")
        for child in children:
            s = score(child, test_cases)
            offspring.append((s, child))
            marker = "+" if s > parent_score else " "
            print(f"    {marker} {s:7.3f}  {child}")

    return offspring


def next_population(population, offspring, pop_size):
    combined = list(population) + offspring
    seen = set()
    new_pop = []
    for entry in sorted(combined, reverse=True):
        score_val, regex = entry
        if regex not in seen:
            seen.add(regex)
            new_pop.append(entry)
            if len(new_pop) == pop_size:
                break
    return new_pop


def sample_parent(population):
    scores = [s for s, _ in population]
    min_s = min(scores)
    weights = [s - min_s + 0.1 for s in scores]
    return random.choices(population, weights=weights, k=1)[0]


def mutate(parent, description, examples, n):
    prompt = build_mutation_prompt(description, examples, parent)
    return generate_candidates(prompt, n)


def build_mutation_prompt(description, examples, parent):
    parent_score, parent_regex = parent
    lines = [description, "", "Examples:"]
    for input_string, expected in examples:
        verdict = "MATCH" if expected else "NO MATCH"
        lines.append(f"  {input_string!r:12}  ->  {verdict}")

    lines.append("")
    lines.append("Here is one regex pattern that has been tried:")
    lines.append(f"  Score: {parent_score:.3f}")
    lines.append(f"  Pattern: {parent_regex}")
    lines.append("")
    lines.append(
        "Propose new regex patterns that are variations or improvements "
        "of this one. Each should try a different mutation: drop "
        "characters, change structure, simplify, or take a different "
        "approach. Aim to beat the parent's score."
    )
    return "\n".join(lines)


def seed_population(description, test_cases, examples, target_size):
    _, _, all_scored = best_of_n(
        description, test_cases, examples, n=target_size + 10
    )
    seen = set()
    unique = []
    for entry in sorted(all_scored, reverse=True):
        score_val, regex = entry
        if regex not in seen:
            seen.add(regex)
            unique.append(entry)
            if len(unique) == target_size:
                break
    return unique


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

    history = evolutionary_search(
        description=description,
        test_cases=cases,
        examples=examples,
        pop_size=20,
        n_generations=5,
        parents_per_gen=5,
        offspring_per_parent=3,
    )

    print(f"\n{'=' * 70}")
    print("CONVERGENCE — best score after each generation")
    print(f"{'=' * 70}")
    for gen, pop in history:
        best_score, best_regex = max(pop)
        gen_label = "Seed" if gen == 0 else f"Gen {gen}"
        print(f"{gen_label:>6}: {best_score:7.3f}  {best_regex!r}")

    print(f"\n{'=' * 70}")
    print("FINAL POPULATION")
    print(f"{'=' * 70}")
    final_pop = history[-1][1]
    for s, candidate in final_pop:
        print(f"  {s:7.3f}  {candidate}")

    final_best = max(final_pop)
    print(f"\nFinal winner: {final_best[1]!r}  (score {final_best[0]:.3f})")
