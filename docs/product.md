# Product: Burning Cinema Box Office

## Identity

**Burning Cinema – Hochschulkino Deggendorf e.V.**
Registered association (Amtsgericht Deggendorf, VR 200613).
University-affiliated (THD rooms, THD contact infrastructure) but legally independent.

## What it is

A volunteer-operated point-of-sale and event-management tool for a small university
cinema club. Covers the full lifecycle of a screening night: movie setup, door sales
(tickets + snacks), order tracking, and treasurer reporting.

Key characteristics:
- One venue, one screen, one event at a time
- ~100–300 seats per screening
- Infrequent events (not a daily operation)
- Operated by volunteers under real-time pressure at the door

## Users

| Role | Who | What they need |
|------|-----|----------------|
| Cashier | Member at the door | Fast POS — keyboard-operable, minimal clicks, no ambiguity |
| Admin | Board member / event organiser | Movie CRUD, inventory management, pricing |
| Treasurer (Kassenwart) | Elected board role | Per-event revenue report, cancellation audit trail |
| Member (Mitglied) | Association member buying at the door | Discounted pricing (Mitgliederpreis) via team mode — no separate login |

## Out of scope

The following are explicitly not part of this system:

- Public-facing ticket booking website
- Online payment / payment terminal integration (Stripe is a future option, not MVP)
- Streaming or digital content delivery
- Multi-venue or multi-screen operation
- Loyalty programmes or member accounts
- Mobile-first or native app

## Scale ceiling

- Single concurrent cashier session per screening
- Tens of orders per event, not thousands
- One admin at a time; no concurrent editing conflicts expected

## Language

UI strings are **German-first** — Vereinsmitglieder are German speakers and operate
under time pressure. API field names, database schema, and source code stay English.
