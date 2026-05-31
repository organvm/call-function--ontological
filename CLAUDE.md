# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository implements the **FUNCTIONcalled()** naming and metadata convention — a system for self-documenting file names and metadata sidecars. The core principle is that names should be **autological** (self-descriptive), containing their purpose, role, and context without requiring external lookup.

## Naming Convention

**Repository names:** Use `call-{name}--{descriptor}` format
- Single hyphen (`-`) separates words within a segment
- Double hyphen (`--`) separates the function name from its descriptor

**File names:** Pattern `{Layer}.{Role}.{Domain}.{Extension}`
- Versions must follow semver format (e.g., `1.0.0`, `2.1.3-beta.1`)

## Commands

```bash
# Install dependencies
make install-deps          # Installs jsonschema + semgrep

# Validate metadata files
make validate              # Validates *.meta.json against the schema

# Validate file naming conventions
make validate-naming       # Checks files follow {Layer}.{Role}.{Domain}.{ext}

# Run semgrep rules
make semgrep               # Validates header comments structure

# Run ALL validators
make validate-all          # Runs validate + validate-naming + semgrep

# Build the registry
make registry              # Scans for .meta.json files, outputs registry/registry.json

# Install pre-commit hook
make hook-install          # Runs all validators on git commit
```

To validate specific files directly:
```bash
python tools/validate_meta.py path/to/file.meta.json
python tools/validate_naming.py path/to/file.ext
```

## Architecture

### Layer System

Files follow the naming pattern `{Layer}.{Role}.{Domain}.{Extension}`. The four canonical layers are:

| Layer | Alias | Purpose | Languages |
|-------|-------|---------|-----------|
| `core` | `bones` | Foundation, kernel, structure | C, C++, Rust, Go |
| `interface` | `skins` | Portals, surfaces, UI | HTML, CSS, JS, PHP |
| `logic` | `breath` | Scripts, intelligence, agents | Python, Lua, Ruby |
| `application` | `body` | Embodiment, apps, bridges | Swift, Obj-C, Java |

Each layer directory contains starter `template.*` files with header comments describing the role.

### Metadata Sidecar Pattern

Any file can have a companion metadata sidecar named `{filename}.meta.json`. The schema supports two profiles:

- **light**: Minimal required fields (`profile`, `name`, `identifier`, `version`)
- **full**: Extended fields including `schema:type`, `conformsTo`, `encodingFormat`, `dateCreated`, `dateModified`

Schema: `standards/FUNCTIONcalled_Metadata_Sidecar.v1.1.schema.json`

### Registry

The registry builder (`tools/registry-builder.py`) walks the repo, finds all `.meta.json` files, and generates `registry/registry.json` — a catalog of all tracked resources with paths and optional SHA256 hashes.

## Commit Message Format

```
[layer:role] action — scope
```

Example: `[breath:agent] improve inference — caching`

<!-- ORGANVM:AUTO:START -->
## System Context (auto-generated — do not edit)

**Organ:** ORGAN-I (Theory) | **Tier:** standard | **Status:** GRADUATED
**Org:** `organvm-i-theoria` | **Repo:** `call-function--ontological`

### Edges
- **Produces** → `unspecified`: theory

### Siblings in Theory
`recursive-engine--generative-entity`, `organon-noumenon--ontogenetic-morphe`, `auto-revision-epistemic-engine`, `narratological-algorithmic-lenses`, `sema-metra--alchemica-mundi`, `cognitive-archaelogy-tribunal`, `a-recursive-root`, `radix-recursiva-solve-coagula-redi`, `.github`, `nexus--babel-alexandria`, `4-ivi374-F0Rivi4`, `cog-init-1-0-`, `linguistic-atomization-framework`, `my-knowledge-base`, `scalable-lore-expert` ... and 10 more

### Governance
- Foundational theory layer. No upstream dependencies.

*Last synced: 2026-05-23T00:26:31Z*

## Active Handoff Protocol

If `.conductor/active-handoff.md` exists, **READ IT FIRST** before doing any work.
It contains constraints, locked files, conventions, and completed work from the
originating agent. You MUST honor all constraints listed there.

If the handoff says "CROSS-VERIFICATION REQUIRED", your self-assessment will
NOT be trusted. A different agent will verify your output against these constraints.

## Session Review Protocol

At the end of each session that produces or modifies files:
1. Run `organvm session review --latest` to get a session summary
2. Check for unimplemented plans: `organvm session plans --project .`
3. Export significant sessions: `organvm session export <id> --slug <slug>`
4. Run `organvm prompts distill --dry-run` to detect uncovered operational patterns

Transcripts are on-demand (never committed):
- `organvm session transcript <id>` — conversation summary
- `organvm session transcript <id> --unabridged` — full audit trail
- `organvm session prompts <id>` — human prompts only


## System Library

Plans: 269 indexed | Chains: 5 available | SOPs: 8 active
Discover: `organvm plans search <query>` | `organvm chains list` | `organvm sop lifecycle`
Library: `/Users/4jp/Code/organvm/praxis-perpetua/library`


## Active Directives

| Scope | Phase | Name | Description |
|-------|-------|------|-------------|
| system | any | atomic-clock | The Atomic Clock |
| system | any | execution-sequence | Execution Sequence |
| system | any | multi-agent-dispatch | Multi-Agent Dispatch |
| system | any | session-handoff-avalanche | Session Handoff Avalanche |
| system | any | system-loops | System Loops |
| system | any | prompting-standards | Prompting Standards |
| system | any | background-task-resilience | background-task-resilience |
| system | any | context-window-conservation | context-window-conservation |
| system | any | session-self-critique | session-self-critique |
| system | any | the-descent-protocol | the-descent-protocol |
| system | any | the-membrane-protocol | the-membrane-protocol |
| system | any | theory-to-concrete-gate | theory-to-concrete-gate |
| system | any | triangulation-protocol | triangulation-protocol |

Linked skills: SOP-TRIADIC-REVIEW-PROTOCOL, cicd-resilience-and-recovery, continuous-learning-agent, evaluation-to-growth, genesis-dna, multi-agent-workforce-planner, promotion-and-state-transitions, quality-gate-baseline-calibration, repo-onboarding-and-habitat-creation, session-self-critique, structural-integrity-audit, the-membrane-protocol, triple-reference


**Prompting (Anthropic)**: context 200K tokens, format: XML tags, thinking: extended thinking (budget_tokens)


## Atomization Pipeline

Run `organvm atoms pipeline --write && organvm atoms fanout --write` to generate task queue.


## System Density (auto-generated)

AMMOI: 25% | Edges: 0 | Tensions: 0 | Clusters: 0 | Adv: 27 | Events(24h): 37975
Structure: 8 organs / 148 repos / 1654 components (depth 17) | Inference: 0% | Organs: META-ORGANVM:63%, ORGAN-I:53%, ORGAN-II:48%, ORGAN-III:54% +5 more
Last pulse: 2026-05-23T00:26:28 | Δ24h: n/a | Δ7d: n/a


## Dialect Identity (Trivium)

**Dialect:** FORMAL_LOGIC | **Classical Parallel:** Logic | **Translation Role:** The Grammar — defines well-formedness in any dialect

Strongest translations: III (formal), IV (formal), META (formal)

Scan: `organvm trivium scan I <OTHER>` | Matrix: `organvm trivium matrix` | Synthesize: `organvm trivium synthesize`


## Logos Documentation Layer

**Status:** ACTIVE | **Symmetry:** 0.5 (DREAM)

Nature demands a documentation counterpart. This formation maintains its narrative record in `docs/logos/`.

### The Tetradic Counterpart
- **[Telos (Idealized Form)](../docs/logos/telos.md)** — The dream and theoretical grounding.
- **[Pragma (Concrete State)](../docs/logos/pragma.md)** — The honest account of what exists.
- **[Praxis (Remediation Plan)](../docs/logos/praxis.md)** — The attack vectors for evolution.
- **[Receptio (Reception)](../docs/logos/receptio.md)** — The account of the constructed polis.

### Alchemical I/O
- **[Source & Transmutation](../docs/logos/alchemical-io.md)** — Narrative of inputs, process, and returns.



*Compliance: Record exists without implementation.*

<!-- ORGANVM:AUTO:END -->












## ⚡ Conductor OS Integration
This repository is a managed component of the ORGANVM meta-workspace.
- **Orchestration:** Use `conductor patch` for system status and work queue.
- **Lifecycle:** Follow the `FRAME -> SHAPE -> BUILD -> PROVE` workflow.
- **Governance:** Promotions are managed via `conductor wip promote`.
- **Intelligence:** Conductor MCP tools are available for routing and mission synthesis.