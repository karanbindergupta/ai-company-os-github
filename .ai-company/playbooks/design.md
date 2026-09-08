---
playbook: design
version: 1.0.0
---
# Design & Creative Playbook

Operational, not motivational. Follow it.

## 1. How a professional approaches problems here
A product becomes ugly by accumulation - each screen reasonable, the whole incoherent. Your job is to prevent that. Strategy precedes craft: brand strategy, audience, positioning, direction, then execution.

## 2. Standard workflow
1. Read the brand strategy and positioning before opening any canvas
2. Establish or consult the design system - tokens are the source of truth
3. Design structure and flow first (UX), then the visual layer (UI)
4. Design the unhappy path: error, empty, loading, offline
5. Specify keyboard and screen-reader behaviour for every interaction
6. Verify contrast at every token pairing, in light and dark
7. Submit to creative audit for coherence across surfaces, not screen by screen

## 3. Research methodology
Look at how strong products solve the same interaction and extract the principle. Never copy the surface. Check the accessibility standard rather than assuming.

## 4. Decision frameworks
- **Token-first** - if a value is not a token, either add a token or you are inventing a one-off
- **Job-to-be-done per screen** - what is this screen for, in one sentence?
- **Progressive disclosure** - complexity revealed on demand
- **Accessibility wins ties** - when it conflicts with visual preference, accessibility is chosen

## 5. Common failure modes
- **Happy-path-only design** - No error, empty or loading state. Incomplete; will be rejected.
- **One-off components** - Duplicating an existing component with slight differences.
- **Colour-only meaning** - Information conveyed by colour alone.
- **Dark mode as an afterthought** - A colour defined only inside a dark-mode block.
- **Decorative motion** - Animation with no stated purpose, harming performance.

## 6. Quality checklist (run before submitting)
- [ ] Every value resolves to a design token
- [ ] Error, empty and loading states designed
- [ ] Contrast meets WCAG 2.2 AA at every pairing, both themes
- [ ] Full keyboard path with visible focus
- [ ] Nothing conveyed by colour alone
- [ ] Reduced-motion alternative for every animation

## 7. Deliverable templates
- `.ai-company/templates/design-brief.md`
- `.ai-company/templates/ux-specification.md`
- `.ai-company/templates/brand-strategy.md`
- `.ai-company/templates/campaign-brief.md`

## 8. Review checklist (for whoever reviews this work)
- [ ] Does this look like it belongs to the same product as the other screens?
- [ ] What happens when this list is empty, or has 10,000 rows?
- [ ] Can this be operated entirely by keyboard?
- [ ] Is any value here not from the token set?

## 9. Escalation rules
L2 to the Creative Director when a needed component does not exist. L3 when creative direction conflicts with product scope or performance budget.

## 10. Collaboration
Take strategy from brand, constraints from engineering. Hand frontend the tokens and states, not a picture. Accessibility reviews before build - retrofitting is far more expensive.

## 11. Excellent vs unacceptable

**Excellent**
> 'Export modal. States: idle, validating, in-progress with row count, success with download, error with the specific failure and a retry. Tokens: surface-raised, text-primary, accent-600. Focus trapped in modal, Esc closes, focus returns to trigger. Contrast 7.1:1 both themes.'

**Unacceptable**
> 'A clean modern export modal with a nice progress bar.'
