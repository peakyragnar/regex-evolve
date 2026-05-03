# Working constraints for regex-evolve

This is a learning project. The user is building this to learn the AlphaEvolve pattern by implementing it. Optimize for understanding, not for shipping.

## How to work

**Explain before you write.** Before writing any non-trivial piece of code, explain in plain language what you're about to do, why, and what alternatives exist. After explaining, ask if the user wants to proceed before writing the code.

**Keep functions small.** Aim for functions that do one thing and fit on a single screen. If a function is getting longer than ~30 lines or has more than one level of nested logic, split it.

**No premature abstractions.** Do not add base classes, plugin systems, configuration frameworks, or factory patterns until concrete duplication forces them. Two concrete implementations are easier to reason about than one abstract one.

**No unnecessary dependencies.** The full project should run on `google-genai`, `python-dotenv`, and standard library. Anything else needs explicit justification before being added.

**Write code the user can read.** Prefer clarity over cleverness. No list comprehensions when a for-loop is clearer. Variable names should be self-explanatory. Comments explain *why*, not *what*.

**Show output frequently.** Run the code at each step. Show what it produces. Do not write 100 lines of code without running it.

**Surface failures honestly.** When something doesn't work, say so clearly. Don't paper over errors with try/except. Show the actual failures.

**Small commits, frequent checkpoints.** After each meaningful unit of work, suggest committing to git with a clear message.

**Pause for understanding.** At natural breakpoints — end of a phase, after a notable design decision, after seeing a result — pause and ask if the user has questions before moving on.

**Don't optimize prematurely.** No async, batching, caching, or parallelization until the simple version is working.

**Stay in scope.** This project is the toy regex search. If the user mentions something outside the project, note it for later, don't build it now.

## Project context

See `PLAN.md` for the goal, design, build phases, and success criteria.

## Stack

- Python managed by `uv`
- Gemini API via `google-genai`
- Environment via `.env` file (GEMINI_API_KEY)
- Standard library for everything else

## This is the end goal: to master this implementation
https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/

## This is a 3rd party implementation that could be helpful, use as reference, but always defer to alphaevolve implementation
https://github.com/algorithmicsuperintelligence/openevolve