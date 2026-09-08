---
document: design-system
version: 1.0.0
owner: design-system-architect
status: baseline
---
# DESIGN SYSTEM

**The source of truth for product UI.** Every visual value in design and in code resolves to a
token here. A literal colour or spacing value in a component is a defect.

This is a **neutral baseline**. When a mission sets brand direction, the Brand Designer replaces
the palette and type scale; the structure and rules below stay.

## Tokens

### Colour — semantic, never raw
| Token | Light | Dark | Use |
|---|---|---|---|
| `--bg` | `#fcfcfd` | `#0b0d10` | Page ground |
| `--surface` | `#ffffff` | `#14171c` | Cards, panels |
| `--surface-raised` | `#f6f7f9` | `#1c2027` | Modals, popovers |
| `--border` | `#e4e7ec` | `#2a2f38` | Dividers, outlines |
| `--text` | `#12151a` | `#eef1f5` | Primary text |
| `--text-muted` | `#5b6472` | `#98a2b3` | Secondary text |
| `--accent` | `#2f5fe0` | `#6b8ff5` | Primary action |
| `--accent-text` | `#ffffff` | `#0b0d10` | Text on accent |
| `--success` | `#137a4a` | `#3fbf85` | Confirmation |
| `--warning` | `#9a6300` | `#e0a137` | Caution |
| `--danger` | `#b4232b` | `#f2646c` | Destructive, errors |
| `--focus` | `#2f5fe0` | `#8fb0ff` | Focus ring |

**Every pairing above meets WCAG 2.2 AA (4.5:1 body, 3:1 large/UI) in both themes.** Changing a
value requires re-verifying contrast — the Accessibility Designer signs that off.

### Type
`--font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
`--font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace`

| Token | Size / line-height | Use |
|---|---|---|
| `--text-xs` | 12 / 16 | Labels, captions |
| `--text-sm` | 14 / 20 | Secondary, dense tables |
| `--text-base` | 16 / 24 | Body — never smaller for prose |
| `--text-lg` | 18 / 28 | Lead paragraphs |
| `--text-xl` | 22 / 30 | Section headings |
| `--text-2xl` | 28 / 36 | Page titles |
| `--text-3xl` | 36 / 44 | Hero |

Weights: 400 body, 500 UI labels, 600 headings. No other weights without an ADR.

### Spacing — 4px base, no arbitrary values
`--space-1:4` `--space-2:8` `--space-3:12` `--space-4:16` `--space-5:24` `--space-6:32`
`--space-7:48` `--space-8:64` `--space-9:96`

### Radius / elevation / motion
`--radius-sm:6` `--radius-md:10` `--radius-lg:16` `--radius-full:9999`
`--elev-1: 0 1px 2px rgb(0 0 0 / .06)` · `--elev-2: 0 4px 12px rgb(0 0 0 / .08)` ·
`--elev-3: 0 12px 32px rgb(0 0 0 / .12)`
`--motion-fast:120ms` `--motion-base:200ms` `--motion-slow:320ms`, easing `cubic-bezier(.2,.7,.3,1)`

**Every animation needs a reduced-motion alternative** under `prefers-reduced-motion: reduce`.

### Grid
4px base · 12-column · gutters `--space-5` · max content width 1200px ·
breakpoints 480 / 768 / 1024 / 1280.

## Required states — a component without all of these is incomplete
`default` · `hover` · `active` · `focus-visible` · `disabled` · `loading` · `error` ·
`empty` · `read-only` (where applicable)

## Component contract
Every component specifies: purpose, anatomy, variants, all states above, keyboard interaction,
ARIA semantics, responsive behaviour, and the tokens it consumes. **A new component requires
justification against existing ones** — the Design System Architect may reject a duplicate.

Baseline set: button, input, select, checkbox, radio, textarea, form field with error, table,
card, modal, drawer, tooltip, toast, tabs, accordion, breadcrumb, pagination, avatar, badge,
banner, empty state, loading skeleton, navigation.

## Non-negotiable rules
1. No literal colour, spacing, radius or duration in any component — tokens only.
2. Light and dark both defined. Never define a colour only inside a dark-mode block.
3. Contrast verified at every pairing, both themes.
4. Every interaction reachable and operable by keyboard, with visible focus.
5. Nothing conveyed by colour alone.
6. Error messages say what happened **and what to do next**.
7. Every empty state offers an action — no dead ends.
8. Motion has a stated purpose and a reduced-motion alternative.
