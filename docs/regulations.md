# German Legal Requirements

Burning Cinema – Hochschulkino Deggendorf e.V. is a registered association
(eingetragener Verein) operating in Bavaria. This document records the relevant
legal requirements and their implications for the software. It is not legal advice;
confirm specifics with a Steuerberater or Rechtsanwalt before going live.

## KassenSichV / §146a AO — Kassensicherungsverordnung

**What it is**: Since 1 January 2020, electronic cash registers used for taxable
transactions in Germany must be equipped with a certified Technical Security Device
(Technische Sicherheitseinrichtung, TSE) that cryptographically signs each transaction.

**Applies to Burning Cinema?**: Likely yes, because the Verein sells tickets and
consumables for money. As a gemeinnütziger Verein, certain ideelle (non-commercial)
activities may qualify for an exemption, but commercial activities (Zweckbetrieb,
wirtschaftlicher Geschäftsbetrieb) generally do not. **Confirm with Steuerberater.**

**Software implications**:
- Order records must be **append-only** — no deletion of History documents
- Timestamps must be set **server-side** at the moment of sale, not by the client
- The architecture must not block a future TSE integration (e.g., a signing layer
  added between order creation and persistence)
- If a TSE module is added later, it will need the order total, timestamp, and a
  transaction sequence number — design the Order model to accommodate these fields

## DSGVO — Datenschutz-Grundverordnung (GDPR)

**What it is**: EU data protection regulation, implemented in Germany alongside
BDSG (Bundesdatenschutzgesetz).

**Personal data this system processes**:

| Data | Where | Legal basis |
|------|-------|-------------|
| Email address | Reservation | Contract performance (§6 Abs.1 lit.b DSGVO) |
| Seat number | Reservation | Contract performance |
| Purchase totals | Order (History) | Legitimate interest — Vereinsbuchhaltung |

**Retention**:
- Reservation data (email, seat) must not be kept indefinitely. Suggest purging
  email addresses 30 days after the screening date.
- Financial records (Order totals) are subject to the 10-year GoBD retention —
  see below. These contain no personal data in their current form.

**Software implications**:
- Add `retention_until` or derive it from `Movie.datetime` for Reservations
- Provide an admin action to anonymise/delete reservation PII after the event
- The Verein must maintain a Datenschutzerklärung and Verzeichnis von
  Verarbeitungstätigkeiten — this is the Verein's obligation, not the software's,
  but the software must not make it harder to comply

## GoBD — Grundsätze zur ordnungsmäßigen Führung von Büchern

**What it is**: German tax authority requirements for electronic bookkeeping records.

**Key rules**:
- Financial records must be retained for **10 years**
- Records must be **unalterable after the fact** — no retroactive editing of order
  data, no silent deletes
- Records must be exportable in a machine-readable format (the Excel report
  export satisfies this; MongoDB records are the primary archive)

**Software implications**:
- `Order.cancellation` is a status flag — the original record always remains
- No `DELETE` endpoint on the History (Order) collection
- The report download covers the readable-format requirement

## Umsatzsteuer — VAT

**Rates that apply**:

| Item type | VAT rate | Basis |
|-----------|----------|-------|
| Cinema tickets (cultural event) | **7%** reduced | §12 Abs.2 Nr.7a UStG |
| Food and drinks (event service) | 19% standard (verify) | §12 UStG |

**Kleinunternehmerregelung** (§19 UStG): If the Verein's total annual turnover
(all revenue, not just cinema) is below **€22,000**, it may be exempt from VAT
reporting entirely. Confirm current status with treasurer.

**Software implication**: The current system does not track VAT per item or
category. Before the rewrite ships, the team must decide:
- Option A: add `vat_rate` to Inventory items and include VAT breakdown in reports
- Option B: document an explicit decision that VAT is handled externally by the
  treasurer and the software intentionally omits it

This decision must be recorded here once made.

## Vereinsrecht — BGB §§ 21–79

**Treasurer (Kassenwart) obligations** that the software must support:
- Per-event revenue summary — covered by the `/report` endpoint
- Visibility into cancellations — covered by the cancellation flag and report
- Annual Kassenbericht across all events — **currently missing**; the rewrite
  should add date-range aggregation across multiple movies

No other Vereinsrecht obligations directly constrain the software.
