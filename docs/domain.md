# Domain Model

This document maps the real-world concepts of a Burning Cinema screening night to
the software model. German terms are the source of truth for naming; English is used
in code.

## Core concepts

| German term | Model / field | Notes |
|-------------|---------------|-------|
| Vorführung | `Movie` | One screening event — unique name, room, datetime |
| Kassensitzung | POS session | Implicit: one cashier, one Movie selected |
| Artikel | `Inventory` item | A sellable item — ticket, drink, snack, Pfand |
| Warengruppe | `Category` enum | `TICKETS`, `DRINKS`, `SNACKS`, `SWEETS`, `PFAND` |
| Bestellung | `Order` (History) | One completed cart transaction at the door |
| Stornierung | Cancellation | Soft flag on an Order — records are never deleted |
| Pfand | Pfand item | Bottle deposit — special category, auto-managed by cart |
| Mitgliederpreis | `price_team` | Discounted price for association members |
| Kassenbon | Order receipt | Not currently printed; captured as History record |
| Reservierung | `Reservation` | Seat reservation linked by email; no user account |

## Relationships

```
Movie
  └── has many Orders (History)
        └── each Order contains Products[] (snapshot of Inventory items)
  └── has many Reservations

Inventory
  └── has Category (TICKETS | DRINKS | SNACKS | SWEETS | PFAND)
  └── has price (Gastpreis) and price_team (Mitgliederpreis)
```

Orders store a **snapshot** of product name, price, and category at the time of
sale. They do not reference live Inventory documents — this is intentional (prices
may change between events).

## Business rules

These rules must be preserved in any rewrite:

1. **Pfand auto-management**: adding any `DRINKS` item auto-adds the `PFAND` item
   to the cart; removing all drinks removes Pfand. Pfand is suppressed in team mode.

2. **Team mode**: switches all cart prices to `price_team` and suppresses Pfand.
   Toggling team mode mid-cart recalculates all prices in place.

3. **Cancellation is a flag**: `Order.cancellation = true` is the only way to void
   an order. No Order is ever deleted (GoBD requirement).

4. **Revenue separation**: reports must distinguish team-mode revenue from guest
   revenue, and can optionally exclude Pfand from totals.

5. **Inventory tracking**: each sale decrements `Inventory.amount` and increments
   `Inventory.amount_sold`. These are informational — no hard stock enforcement
   at the POS (cashier decides if out of stock).

6. **Reservation scanning**: each `Reservation` can be scanned exactly once
   (`scanned = true`). Re-scanning must return an error, not silently succeed.

## Named products with special meaning

The following product names carry semantic meaning in business logic and reports.
They must remain stable or be replaced with a proper type/flag system:

| Product name | Meaning |
|--------------|---------|
| `Ticket` | Standard guest ticket (counts toward ticket sold total) |
| `Freiticket` | Complimentary ticket (counted separately in reports) |
| `Pfand` | Bottle deposit (auto-cart; excluded from some revenue totals) |
| `Pfand Rück` | Deposit return (negative revenue line) |

Hardcoding product names as strings is a known fragility. The rewrite should
replace these with an explicit field or category flag.
