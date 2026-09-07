---
name: parallel-dispatch
description: How to decide what runs in parallel and dispatch it correctly. Load when planning a phase, building a task graph, or dispatching multiple agents. Covers dependency analysis, the fan-out/fan-in pattern, and worktree isolation.
---

# Parallel dispatch

Serializing independent work is a defect. Parallelizing dependent work is a worse one.

## The test
Two tasks may run in parallel if **neither consumes an artifact the other produces**, and they do
not write the same files. That is the whole rule.

## What is genuinely independent here
| Parallel | Why |
|---|---|
| All six research roles | Each reads the mission; none reads another's output |
| Executive positions in a debate | Independence is the point - they must not see each other first |
| Architecture and design | Both depend on the product spec, neither on the other |
| QA and security | Both depend on integration, neither on the other |
| The four audits | Independent by design |

## What only looks independent
| Not parallel | Why |
|---|---|
| Backend and frontend, before the API contract | Both invent incompatible contracts; work is redone |
| Design and product spec | Design consumes requirements |
| Business model and market research | The model needs the sizing |
| Anything and its own review | Review consumes the output |

## Dispatching
**Put every parallel task in a single message.** Multiple `Agent` calls in one response run
concurrently. Calls in separate messages run one after another - that is the most common way
parallelism is silently lost.

```bash
python3 scripts/company.py ready     # shows dispatchable tasks, already grouped
```

## Fan-out, fan-in
1. Fan out the group in one message
2. Collect the summaries (not the artifacts - those are on disk)
3. Reconcile conflicts; send real disagreements to the CEO rather than averaging them
4. Only then start the dependent group

## File collisions
When parallel workstreams touch the same files, use `EnterWorktree` for isolation. Two agents
editing one file concurrently will lose work.

## Do not over-parallelize
Every parallel agent costs tokens and produces a summary someone must read. Four well-chosen
parallel researchers beat twelve overlapping ones.
