# Design Foundation

This document defines the principles, constraints, and existing tokens that the
design system will be built on. Specific tokens, components, and patterns are
defined in a dedicated design-system branch — this file provides the stable
foundation that branch works from.

## Identity

**Product**: Burning Cinema – Hochschulkino Deggendorf
**Feeling**: cinematic, warm, confident — not clinical or corporate
**Audience**: volunteers operating under real-time event pressure

Design for **speed and low error rate**, not visual novelty. A cashier selling
tickets at the door has no patience for ambiguity.

## Interface contexts

| Context | Device | Priority |
|---------|--------|----------|
| POS / cashier | Desktop or laptop, keyboard-first | Speed, large targets, unambiguous affordances |
| Admin / movie management | Desktop | Information density acceptable |
| Statistics / reporting | Desktop | Readability, printable layout |
| Mobile | Out of scope for current rewrite | — |

## Principles

**1. Keyboard-first POS**
Every cashier action must be reachable without a mouse. The numeric keypad,
cart manipulation, and checkout flow must all be fully keyboard-navigable.
Do not rely on hover states for any action in the POS view.

**2. Fail loudly in German**
No silent errors. Every failed API call must produce a visible, German-language
message that tells the cashier what went wrong and what to do next. `console.log`
is not error handling.

**3. Stateless views**
No hidden component state that survives a page refresh, except `selectedMovie`
(persisted intentionally to localStorage so a page reload mid-event doesn't lose
context). Everything else should be re-fetchable from the API.

**4. One language boundary**
UI strings: German. Code, API field names, schema, commit messages: English.
Do not mix languages within a single layer.

**5. No dead states**
Every screen must have a defined empty state (no movies, empty cart, no orders)
that guides the user to the next action rather than showing a blank panel.

## Existing visual tokens

These are the canonical tokens derived from the current Vuetify theme. They are
the source of truth until a Figma design system is created, at which point the
Figma tokens take precedence and this table is superseded.

| Token name | Value | Purpose |
|------------|-------|---------|
| `color-primary` | `#EF605A` | CTAs, active states, brand accent (warm red) |
| `color-secondary` | `#07A0C3` | Informational elements, secondary actions (cyan) |
| `color-background` | `#898989` | App background surface |
| `theme` | Dark | All surfaces use the dark Vuetify theme |

## What the design system branch will define

The next dedicated branch will build on this foundation and specify:

- Full color token set (surface hierarchy, error, warning, success states)
- Typography scale (typeface, sizes, weights, line heights)
- Spacing and layout grid
- Component usage map: which Vuetify components to use as-is, which to wrap,
  which to replace
- POS-specific interaction patterns: keypad input, cart line items, checkout flow
- Form and validation patterns (error states, German error copy)
- Data display patterns for the statistics and admin views
