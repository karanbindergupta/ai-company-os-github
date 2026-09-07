---
document: model-routing
version: 1.0.0
status: policy defined; single-provider execution today
---
# MODEL ROUTING

The organization is **model-agnostic by construction**: roles, tasks, gates and artifacts contain
no provider assumption. Swapping the execution model changes no governance.

## Honest current state
Only Claude executes in this environment. **No abstraction layer was built for providers that
cannot run here** — that would be architecture for appearance, which section 43 forbids. What
exists is the routing *policy*, so the layer can be added when a second provider is genuinely
available.

## Routing dimensions
reasoning depth · coding capability · speed · cost · context length · multimodal need ·
research capability · privacy sensitivity · reliability.

## Policy by work class
| Work | Needs | Route to |
|---|---|---|
| Executive judgement, debate, rulings | Deep reasoning, long context | Highest-capability model |
| Architecture, security, adversarial review | Deep reasoning, precision | Highest-capability model |
| Research execution, drafting, testing | Throughput, good-enough reasoning | Mid-tier model |
| Mechanical transforms, formatting, extraction | Speed and cost | Smallest sufficient model |
| Anything touching credentials or production | **Reliability over cost** | Highest-capability, never routed down |

Subagent definitions already carry a `model:` field, so per-role routing is live today within
one provider — `opus` for judgement-heavy roles, `sonnet` for execution-heavy ones.

## Rules
1. **Never route a security or release decision to a cheaper model** to save cost.
2. Route by task class, not by who is asking.
3. If a provider is unavailable, fall back and **record the substitution in the artifact** —
   a reader must know which model produced a conclusion.
4. Do not build multi-provider machinery until a second provider is actually configured.
