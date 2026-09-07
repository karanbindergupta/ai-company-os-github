---
artifact: competitive-analysis
role: competitor-intelligence
name: Silvia Marchetti
phase: discovery
status: partial
confidence: MEDIUM-HIGH
volatility: HIGH
retrieved: 2026-09-08
refresh_after: 2026-10-08
---
# Competitive landscape — diaspora flight booking

## Summary
**The space is not empty, and the founder's idea as stated already exists and is shipping.**
Four categories of incumbent, all with something we would have to build. The uncontested ground
is not "easier booking" — it is a **search axis nobody currently uses**.

## Direct competitors

### BharatFare — the founder's idea, already launched
[S4, TIER 2 launch announcement + own site, Dec 2025]
WhatsApp-first UK–India flight booking for NRIs, students and families. Dual entities
(UK Ltd + India Pvt Ltd). Amadeus APIs for inventory, Stripe for payments. Planning a
**QR-code campaign in Southall, Hounslow, Wembley, Ilford and Slough** — precisely the
distribution the founder would target.

**This is the same idea, roughly nine months ahead.** FACT, from their own launch material.

### SastiFlight — UK–Pakistan, fully accredited
[S5, own site, TIER 2]
**ATOL bonded and IATA accredited.** Searches Amadeus, Sabre and Travelport. Phone-first —
*"call us and a real person answers. No chatbots, no hold queues."* Explicitly states:
*"Calling is often better for complex itineraries, family bookings, or if you need specific
baggage or seat arrangements."*

### Prime Travels — multi-corridor, enquiry model
[S6, TIER 2] ATOL protected. Nigeria, Pakistan, India, Bangladesh **plus Umrah packages**.
Publishes indicative fares, converts by enquiry form rather than instant booking.

### Diaspora AI — African corridor, adjacent wedge
[S7, TIER 2] AI agent for African diaspora combining **flight search with visa guidance and
application tracking**. Early stage. Notably solving a problem the flight-only players ignore.

## The finding that matters most
SastiFlight's own copy reveals what these customers actually optimise for — and it is **not the
headline fare**:

> *"PIA's generous 46kg baggage allowance in economy can make direct flights more economical for
> families travelling with heavy luggage."*
> *"Manchester fares are sometimes cheaper than Heathrow — always worth comparing both"* (for the
> Bradford/Leeds/Sheffield population).

**INFERENCE, confidence MEDIUM:** the decision variable is **total landed cost for a family with
luggage**, not price-per-seat. A £120-cheaper fare that costs £300 in excess baggage is worse, and
no mainstream OTA computes that. Agents do it in their heads — which is exactly why people still call them.

**This is unverified with actual customers.** It is a strong hypothesis drawn from how agents
market themselves, not from talking to travellers.

## What every incumbent has that we would not
ATOL bonding · IATA accreditation · GDS access (Amadeus/Sabre/Travelport) · a phone number a real
person answers. The last one is not a technology problem.

## Provider provenance
Discovery via **Exa**. **Brave was NOT used** — its token returned HTTP 422
SUBSCRIPTION_TOKEN_INVALID on a live query, so the independent second index was unavailable.
These findings are therefore **single-index** and not independently cross-verified.
