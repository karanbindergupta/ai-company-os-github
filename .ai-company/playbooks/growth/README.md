---
playbook: growth
version: 1.0.0
department: growth
---
# GROWTH PLAYBOOK — "How do we grow sustainably?"

Growth does **not** mean "more users at any cost". It means a business that compounds.

```
ACQUISITION + ACTIVATION + RETENTION + REVENUE + REFERRAL + CUSTOMER VALUE
```

Optimizing any one at the expense of the others is not growth — it is borrowing from the future.

| Document | Covers |
|---|---|
| `README.md` | Funnel, ethics, workflow, failure modes |
| `EXPERIMENTS.md` | The experiment framework and what "successful" actually requires |
| `LOOPS.md` | Compounding mechanisms rather than one-time campaigns |
| `ECONOMICS.md` | CAC, LTV, payback — growth is never separable from economics |

**Extends:** `templates/experiment.md`, `experiments` table, `/experiment`,
`knowledge/customer/CUSTOMER-INTELLIGENCE.md`, `playbooks/finance.md`.

## 1. How a growth professional approaches problems
Find where the funnel actually leaks before deciding what to build. Most "growth problems" are
retention problems wearing an acquisition costume — and pouring traffic into a leaky product
makes the economics worse, not better.

## 2. The funnel

### Acquisition
SEO · content · paid · partnerships · referrals · social · communities · outbound ·
product-led. **Every channel names a target metric and an expected cost before any spend.**

### Activation
- What is the **first meaningful action** — the moment the user gets real value?
- **Time to value** — how long from signup to that moment?
- Where is the friction, and which of it is necessary?
- The **activation metric**: one specific, measurable user action. Not "signed up".

### Retention
Repeat usage · habit formation · churn reasons (from customers, not assumption) · engagement
depth · customer success · does the product actually deliver value repeatedly?

### Monetization
Pricing · conversion · ARPU · expansion · upsell · **contribution margin**. Pricing is
founder-required — prepare a recommendation, never a commitment.

### Referral
Referral triggers · incentives · organic sharing · network effects. Ask: *would a user share this
without an incentive?* If not, an incentive buys a transaction, not a loop.

## 3. Standard workflow
1. Instrument first — you cannot improve what is not measured
2. Find the biggest leak with data, not intuition
3. Research the audience, their language and the channel (`research-director`)
4. Form a hypothesis with a **pre-registered** success threshold
5. Check the economics **before** building (`playbooks/growth/ECONOMICS.md`)
6. Run the experiment
7. Interpret honestly — including confounds and segment differences
8. Decide: scale, iterate, or kill
9. Record the learning, especially for failures

## 4. Common failure modes
- **Acquisition-first on a leaky product** — the single most expensive growth mistake
- **Vanity metrics** — signups without activation, traffic without conversion
- **Post-hoc thresholds** — deciding what "success" meant after seeing the result
- **Ignoring segments** — an average that hides one segment improving and another collapsing
- **Growth divorced from economics** — a channel that "works" at a CAC the business cannot afford
- **One-time campaigns mistaken for loops** — no compounding, so it stops when spend stops

## 5. Quality checklist
- [ ] The leak was identified from data, not assumption
- [ ] Hypothesis and success threshold set **before** running
- [ ] CAC/LTV/payback modelled with sourced benchmarks or an explicit range
- [ ] Segment breakdown examined, not just the aggregate
- [ ] Confounds considered
- [ ] Every claim in the copy is defensible
- [ ] No dark pattern, fabricated urgency or fake social proof

## 6. Growth ethics — non-negotiable
**Never** use deceptive claims · fabricated urgency · fake social proof · misleading pricing ·
dark patterns · unauthorized data collection.

Short-term growth that costs long-term trust is a **net loss** the company will pay for later.
The Conversion Optimization Specialist's role pack requires refusing manipulative patterns and
saying why. Constitution §XX: protect the founder's reputation.

## 7. Collaboration
| With | On |
|---|---|
| Creative Director | Ads, landing pages, campaigns — **quality and performance both** |
| CFO | CAC/LTV/payback; a channel is not viable because it converts, only if it converts profitably |
| Product | In-product growth mechanics, activation, onboarding |
| Research Director | Audience, customer language, competitor positioning, channel costs |
| Analytics | Instrumentation defined before launch |

## 8. Excellent vs unacceptable

**Excellent**
> "Activation is the leak: 71% signup→first-project, then 24% →second-project within 7 days.
> Hypothesis: users who import existing data activate at 2x. Threshold set pre-launch: +8pp on
> 7-day second-project rate, n≥400/arm. Result: +11pp overall, but +19pp for teams and −2pp for
> solo users — recommend shipping to teams only. CAC unchanged at $38; payback 4.1 months."

**Unacceptable**
> "We added an onboarding improvement and signups went up 30%. Growth is working — let's scale
> paid spend."
