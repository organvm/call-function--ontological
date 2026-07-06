# Discovery: organvm/call-function--ontological

**Discovery date:** 2026-06-24
**Status:** VALUE CONFIRMED — promoted to ranked tier

## Value Thesis

`call-function--ontological` is a working Python library that provides a unique capability in the organvm estate: it takes any LLM function-calling schema (OpenAI/Anthropic JSON format) and runs three interlocking philosophical analyses — Aristotelian four-causes (material, formal, efficient, final), Heideggerian phenomenology (Dasein, Zuhandenheit, Vorhandenheit), and Peircean semiotics (Representamen, Object, Interpretant) — producing a structured `FullAnalysis` object with 85+ tests passing and a working CLI (`python -m tools.cli analyze/report/concepts`). As agentic AI workloads scale across the estate, this analyzer becomes a reusable pre-flight layer for debugging misaligned tool-use, auto-generating richer tool descriptions, auditing agent decision-making, and building system prompts that make each tool's *telos* explicit to the agent calling it. No other repo in the estate occupies this role. The FUNCTIONcalled() naming convention (`{Layer}.{Role}.{Domain}.{Extension}`) is a second, orthogonal value stream — a cross-language file-organization standard with a JSON Schema metadata sidecar system, validation toolchain, and registry builder — that is mature enough for adoption across ORGAN-I sibling repos today.

## Highest Latent Value

**The `OntologicalAnalyzer` as a reusable tool-use quality layer for multi-agent systems.**

Any agent pipeline in the estate can import `OntologicalAnalyzer`, pass it a tool schema, and get back a structured coverage ratio and grounding report. This is a forcing function for better tool design: low coverage ratios surface tools with unclear telos, weak descriptions, or ambiguous naming — before they cause agent misbehavior at runtime.

## Best First Task

Publish `call-function-ontological` to PyPI (the `pyproject.toml` is already 90% complete) so any ORGANVM agent or pipeline can `pip install call-function-ontological` and `from call_function_ontological import OntologicalAnalyzer`. Add an `[project.scripts]` entry so `ontological analyze <schema.json>` works as a system command. This makes the analyzer a first-class citizen of the estate's toolchain rather than a local import.
