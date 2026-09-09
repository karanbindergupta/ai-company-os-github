---
artifact: mission-compaction
mission: PROJECT ATLAS (run_a2d1d5010d) — airline / travel distribution
status: CLOSED — full working set deleted by founder instruction 2026-09-09
compacted_from: ~13,300 lines across 70+ artifacts
retrieved: 2026-09-09
---
# PROJECT ATLAS — compacted record

The full working set (competitor dossier, debate transcript, executive positions, audits,
research, finance, product, strategy) was **deleted by founder instruction to save context**.
This file is what survives. It keeps only what would change a future decision.

---
## THE MARKET
Europe → South Asia diaspora air distribution. Reference competitor: **MyFlighty**
(S.C.A. Corporate Group SRL, Civitanova Marche, Italy). Multi-branch Italian travel agency selling
Italy→India, WhatsApp-first, with a B2B sub-agent network.

## THE FIVE FINDINGS THAT WOULD CHANGE A DECISION

**1. The moat is commercial, not technical.**
Negotiated VFR (visiting friends & relatives) and LBR (labourer) fare agreements across **20+
carriers**, plus contracted group block space, plus physical branches. Their platform was built
cheaply — the founder, who knows one of their founders, confirmed it.
*Building better software does not take a single customer.*

**2. Negotiated fares are filed against a PCC, not granted by a GDS.**
Founder's own operator experience: his office ID returned **public fares only**; all negotiated and
VFR content lived in the wholesaler's **mother office ID**, where pricing, holding and issuance
happened. Corroborated by Travelport's CAT35 documentation. Consequence: a fresh GDS contract on
your own office returns public fares and nothing else.

**3. Contribution per ticket on public fares is NEGATIVE.**
Measured, not modelled: sub-agent markup **€5–15/ticket**, commission on public GDS content **≈€0**,
PSP fees on a €725 booking **€15–22**. CFO's conclusion: *capital does not change the sign of a
negative number.* The one observed exception is **group/block fares — €280 cost → €350 retail = €70,
4.7× the regular markup.** If Atlas ever restarts, group product is where the margin is.

**4. Sub-agents are never paid commission and mostly do not know it exists.**
Airline back-end overrides (1–5%, volume- and share-based) accrue to the wholesaler. The sub-agent
sees "Commission 0" and believes that is the whole truth. This is the sharpest commercial wedge
found, and it is why the free-tool model works: the tool is a volume-aggregation machine.

**5. MOTO is SCA-exempt; a web checkout is not.**
The diaspora agent taking payment by telephone skips 3-D Secure while a self-service checkout
legally cannot. The incumbent's phone channel converts better **by regulation**.

## STRUCTURAL CONCLUSIONS
- **Do not compete on "easier/faster/more automated."** Two independent missions reached this:
  structural moats beat UX moats.
- **CEO ruled B2B only**, rejecting B2C and D2C. **Founder overrode** to pursue both B2B
  intelligence and B2B distribution, Europe-wide.
- **Four of five proposed novel revenue models were killed** by adversarial review: override pooling
  (sub-agents never ticket on their own PCC, so there is no distributed volume to pool); allotment
  exchange (unsold block space does not generally expire — carriers allow release); credit bureau
  (GDPR / credit-reporting registration); dummy tickets (IATA Res 830a treats speculative bookings
  as ADM-triggering even in the legitimate form). Only **fare-rule intelligence** survived, and only
  as a wedge.
- **Aggregators (Duffel/Mystifly) remove accreditation and settlement liability**, but Duffel's
  published take (≈€7.80–17.80 on a €500 ticket) **exceeds the market's own markup**, and Duffel
  returns no fare-rule text — removing the raw material for the one surviving model. Air India and
  ITA Airways are absent from its published carrier list.

## OPEN AND UNANSWERED
- **ESC-004** — how the company obtains competitive fare access. Never resolved.
- **ESC-006** — reopened after the founder disclosed capital. **The CEO never ruled.** Four
  executive positions were filed and are now deleted.
- Whether hosted/consolidator PCC arrangements grant **programmatic** access or portal-only.
- Where the incumbent's group block space is sourced.

## RULES THIS MISSION PRODUCED — these outlive it
- **D-9 reinforced:** run the competitive scan before scope. It killed two ideas cheaply.
- **Founder testimony outranks desk research** in a market he has operated in. It corrected the
  company three times: sub-agent commission, build cost, and the PCC mechanism.
- **Absence of a public claim is not evidence of absence of capability.** Of 20 presumed competitor
  frictions, zero were confirmed; the single confirmed gap came from the incumbent's own marketing.

**Do not reconstruct the deleted artifacts. If Atlas restarts, start here and re-verify — the market
moves, and the incumbent shipped a payments flow inside our research window.**
