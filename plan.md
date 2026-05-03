Here's the updated handoff document with the constraints integrated. Paste this whole thing into Claude Code.

---

# Project: regex-evolve

## Goal

Build a small, working AI-driven evolutionary search system that finds regex patterns matching specified test cases. The purpose is to learn the AlphaEvolve pattern (frozen LLM + verifier + evolutionary search) by implementing it from scratch on a toy problem.

This is a learning project, not a product. The output is working code, intuition for how AI search loops behave, and a foundation for applying the same pattern to real problems later.

## Working constraints — read this first

The user is learning the pattern by building it. Optimize the project for that, not for shipping a finished tool.

**Explain before you write.** Before writing any non-trivial piece of code, explain in plain language what you're about to do, why, and what alternatives exist. The user wants to understand each design decision, not just receive working code. After explaining, ask if they want to proceed before writing the code.

**Keep functions small.** Aim for functions that do one thing and fit on a single screen. If a function is getting longer than ~30 lines or has more than one level of nested logic, split it. The user should be able to read any function and understand it in under a minute.

**No premature abstractions.** Do not add base classes, plugin systems, configuration frameworks, or factory patterns until concrete duplication forces them. If something might need to be flexible later, write it inflexibly now and refactor when the second use case appears. Two concrete implementations are easier to reason about than one abstract one.

**No unnecessary dependencies.** Do not add a library to do something the standard library handles. Do not add a library because it's nicer than the obvious approach. Every new dependency should be justified out loud before being added. The full project should run on `google-genai`, `python-dotenv`, and standard library — anything else needs an explicit reason.

**Write code the user can read.** Prefer clarity over cleverness. No list comprehensions when a for-loop is clearer. No one-liners when two lines explain the intent better. Variable names should be self-explanatory. Comments should explain *why*, not *what*.

**Show output frequently.** When building incrementally, run the code and show what it produces at each step. Do not write 100 lines of code without running it. The user learns from seeing actual outputs, including failures.

**Surface failures honestly.** When something doesn't work, say so clearly. Don't paper over errors. Don't add try/except blocks just to hide problems. If the LLM returns garbage, show the garbage and discuss why.

**Small commits, frequent checkpoints.** After each meaningful unit of work, suggest committing to git with a clear message. The user should be able to see the history of how the project was built.

**Pause for understanding.** At natural breakpoints — end of a phase, after a notable design decision, after seeing a result — pause and ask if the user has questions before moving on. The pace should be set by the user's understanding, not by speed of completion.

**Don't optimize prematurely.** No async, no batching, no caching, no parallelization until the simple version is working and the user has seen its behavior. Optimization is a separate phase, not a default.

**Stay in scope.** This project is the toy regex search. Resist scope creep. If the user mentions something interesting that's outside the project, note it for later but don't build it now.

## Background

The AlphaEvolve pattern: a frozen large language model proposes candidate solutions to a problem, an automated verifier scores each candidate against a known objective, and an evolutionary loop selects the best candidates and mutates them to produce the next generation. Over many iterations, the system converges on solutions better than the LLM could produce in one shot.

The novelty doesn't come from training the model. The model's weights stay frozen. The "learning" lives in the system around the model — the accumulated database of verified candidates, the prompts that get refined as patterns emerge, and the search procedure that directs exploration.

This project implements that pattern at the smallest meaningful scale: regex generation against test cases.

## Design

### The problem

Given a list of test cases — each consisting of an input string and an expected boolean (should match / should not match) — find a regex pattern that correctly classifies all cases, optimizing for both correctness and brevity.

### The verifier

A deterministic Python function that takes a candidate regex string and the test cases, returns a score. Scoring rule:
- Each test case the regex correctly classifies adds points
- Pattern length subtracts a small penalty (favor concise solutions)
- Invalid regex (raises an exception when compiled) returns a score of zero

The verifier must be fast (milliseconds per candidate) and fully deterministic.

### The candidate generator

The Gemini API, called as a frozen component. The system sends a prompt containing the problem description and any context (current best candidates, examples of past attempts) and receives N candidate regex strings in response. The model is never trained or fine-tuned.

Model: Gemini 2.5 Flash for the workhorse. Optionally Gemini 3 Pro for occasional higher-quality calls in later iterations.

### The search loop

Three progressively more sophisticated versions, built in order:

**Version 1 — Best-of-N.** Ask Gemini for N candidates in one shot. Score each. Return the best. No iteration.

**Version 2 — Iterative refinement.** Run Best-of-N. Take the top K candidates. Build a new prompt that includes them as context and asks Gemini to improve on them. Run again. Repeat for some number of rounds. Track the best score over time.

**Version 3 — Evolutionary search.** Maintain a population of candidates across rounds. Each round, sample parents from the population (weighted toward higher scores), construct prompts that include parents as context, ask Gemini to generate offspring inspired by the parents. Score offspring, add the best to the population, drop the worst. Track convergence over generations.

### The candidate database

A simple in-memory or SQLite-backed store of every candidate the system has tried. Each entry contains:
- The regex string
- The score
- Which round/generation it came from
- Which parent candidates inspired it (for evolutionary version)

Used to avoid testing the same candidate twice and to feed historical context into prompts.

### The harness

A thin layer that:
- Loads the API key from `.env`
- Calls the Gemini API with retries on transient errors
- Parses N candidate regex patterns out of the model's response
- Logs every call (request, response, tokens used) for later analysis

## Project structure

```
regex-evolve/
├── pyproject.toml
├── .env                          # GEMINI_API_KEY=...
├── .gitignore
├── README.md
├── src/
│   ├── harness.py               # Gemini API wrapper
│   ├── verifier.py              # Scoring function
│   ├── search/
│   │   ├── best_of_n.py        # Version 1
│   │   ├── iterative.py        # Version 2
│   │   └── evolutionary.py     # Version 3
│   ├── database.py              # Candidate storage
│   └── problems/
│       └── examples.py          # Test case definitions
├── runs/                        # Output logs and convergence data
└── notebooks/                   # Optional: analysis of run results
```

Don't create all of these at once. Build files as the project needs them. Empty placeholder files are clutter.

## Test problems

Start with small problems and progressively harder ones. Examples in increasing difficulty:

1. **Match exactly the strings "cat", "dog", "bird"** and reject everything else. Trivial — verifies the pipeline works.

2. **Match valid US ZIP codes (5 digits, optionally followed by dash and 4 digits)** and reject malformed inputs. Tests structural pattern recognition.

3. **Match valid email addresses** against a curated test set with edge cases. Larger search space, real ambiguity.

4. **Classify log lines into "error", "warning", "info"** based on a set of training examples with realistic variation. Tests the system's ability to find compact patterns from messy data.

Each problem is defined as a Python module exporting a list of `(input_string, expected_match)` tuples plus a description string.

## Dependencies

- `google-genai` — Gemini API client
- `python-dotenv` — load API key from `.env`
- Standard library: `re`, `sqlite3`, `json`, `dataclasses`, `pathlib`

No other dependencies for the toy. Resist adding more. If something seems to require a new dependency, surface it for discussion rather than installing.

## Build phases

**Phase A (Day 1-2):** Set up the harness. Project structure, env loading, working `generate_n_candidates(prompt, n)` function that returns a list of regex strings. Verify against problem 1 with a hardcoded prompt — does Gemini reliably return parseable regex candidates?

**Phase B (Day 3-4):** Build the verifier. `score(regex_string, test_cases)` returns a numeric score. Edge cases handled: invalid regex returns 0, empty string handled, length penalty calibrated. Unit tests for the verifier itself.

**Phase C (Day 5-7):** Implement Version 1 (Best-of-N). Combine harness + verifier into an end-to-end run on problem 1. Output: a printed best regex and its score. No iteration yet.

**Phase D (Day 8-10):** Implement Version 2 (iterative refinement). Loop for N rounds. Track best score per round. Plot or print the convergence curve. Run on problems 1 and 2.

**Phase E (Day 11-14):** Implement Version 3 (evolutionary search). Population, parent selection, mutation prompts. Compare convergence rate to Version 2 on problem 3 or 4. Output: convergence curves for both versions side by side.

After each phase: pause, run the code, look at the output together, discuss what worked and what didn't before moving on.

## Success criteria

The project is "done" when:

1. You have a working evolutionary search system that converges on better-than-baseline regex solutions for at least two of the test problems
2. You can articulate, from your own experience, where the system fails and where it works
3. You have convergence curves showing improvement over generations
4. The total code is roughly 300-500 lines of Python — small enough to fit in your head
5. The infrastructure is reusable for the next problem you want to apply this pattern to

## What this project is not

- Not a production system
- Not a competitor to OpenEvolve (which is the mature framework you'd use for real problems later)
- Not optimized for speed or cost — readability and clarity matter more
- Not training any models — all LLM calls use Gemini API with frozen weights
- Not solving regex generation for the world — solving it on small toy problems to learn the pattern

## After this project

Once the toy works and the convergence behavior is visible, the next step is to apply the same architectural pattern to a real problem with a real verifier. That happens in a separate project. The code from this toy may or may not transfer; the intuition definitely will.

## Starting instruction for Claude Code

Read this entire document. Confirm you understand the goal and the working constraints. Then ask the user one question: are they ready to start Phase A, or do they want to discuss any part of the design before beginning?

Do not start writing code until the user confirms.

---

