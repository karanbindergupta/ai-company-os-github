---
name: adversarial-review
description: How to try to break the product before someone else does. Load before release, during the audit phase, and when reviewing any significant design. Concrete failure paths, not speculative worry.
---

# Adversarial review

The purpose is to find what everyone missed because they were all agreeing.

## Ask these, and answer each concretely
**Correctness** — What could fail? Which assumption, if wrong, breaks it? What did we overlook?

**Users** — What would a user abuse? What would a confused user do? What happens when they do the
steps in the wrong order, twice, or on two devices at once?

**Attackers** — What would an attacker exploit? Can one user reach another's data? Is every
endpoint authorized, or only the UI path to it?

**Scale** — What happens at 100x? Which query has no index? What is unbounded — memory, a list, a
loop, a cost?

**Dependencies** — What happens when a third-party API fails, is slow, rate-limits, or returns
something unexpected? Is there a timeout on every call?

**Input** — Malformed, empty, enormous, wrong-typed, hostile, or in a different encoding?

**Concurrency** — Two simultaneous writes? A double-submitted form? A retried payment?

**Environment** — Poor network, offline, an old browser, a small screen, reduced motion, a screen
reader?

**Infrastructure** — What happens when the database is down, a deploy is half-finished, or the
clock is wrong?

## A finding must be concrete
> "Error handling could be better" — **not a finding.**
> "`POST /orders` does not validate `quantity`; a negative value produces a negative total and
> credits the customer" — **a finding.**

Name the input, the path, the observed result, and the impact.

## Every finding becomes a task
Severity, owner, acceptance criteria. Write `.ai-company/audits/adversarial.md`.

**"Everything looks fine" is almost always a failed adversarial review.** Look harder, or say
specifically what you were unable to test and why.
