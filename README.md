# Vantage

[![Status](https://img.shields.io/badge/status-proof--of--concept-orange)]()
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![Streamlit](https://img.shields.io/badge/frontend-streamlit-FF4B4B)]()
[![Supabase](https://img.shields.io/badge/database-supabase-3ECF8E)]()
[![License](https://img.shields.io/badge/license-private-lightgrey)]()

Vantage is a tool for tracking promising operators before they start a company. It surfaces career status changes among senior professionals at high-growth companies, so that early-stage investors can identify potential founders before they are publicly known to be building.

## Problem

Early-stage venture capital is fundamentally a bet on people, not just markets. Investors who can identify a strong founder before that person has publicly committed to starting a company gain a structural advantage: earlier conversations, earlier trust, and access before competing capital arrives.

Today, this kind of sourcing happens almost entirely through informal channels: personal networks, scouts, warm introductions, and analysts manually checking LinkedIn. Existing data platforms do not solve this well. Company-intelligence tools such as Tracxn, Crunchbase, and Dealroom are built for evaluating companies, not tracking individual career trajectories. People-search and sales-intelligence tools such as Apollo are built for outbound sales, not investor sourcing. LinkedIn itself, despite holding the underlying data, is built for recruitment and networking, not systematic monitoring of status changes over time.

The result is an information gap: a meaningful signal exists (a senior operator leaving a company is often a precursor to founding one), but no tool is purpose-built to track that signal at the scale and specificity an investor needs.

## Approach

Vantage treats career status changes as the unit of value, not static profile data. A list of people is a commodity that any data provider can replicate. A notification that a specific, relevant person's status just changed is not.

The system is structured around three layers:

**Tracking.** A defined set of people, generally senior operators and repeat founders at companies with a history of producing founders, is monitored on an ongoing basis.

**Classification.** Each tracked profile is evaluated and labeled against criteria that matter specifically to investors, such as whether someone is a repeat founder, a senior operator, or currently building in stealth, rather than generic attributes like job title or years of experience.

**Detection.** Rather than presenting a static database, the system compares each profile's current state against its last known state and surfaces only meaningful transitions, such as a move from an operating role to an unannounced or stealth status, as alerts.

This reframes the product from a search tool into a monitoring tool. The deliverable is not a list of people; it is an indication that something has changed and may be worth a conversation.

## Architecture
![Uploading stealthscout_backend_combined.png…]()


```
LinkedIn data source
        |
        v
Ingestion and storage (Supabase / Postgres)
        |
        v
Classification pipeline
   - status classification (employed / stealth / founder)
   - signal tagging (repeat founder, senior operator)
        |
        v
Change detection
   - compares current snapshot to prior snapshot
   - writes a new row to the alerts table on a meaningful change
        |
        v
Frontend (Streamlit)
   - alert feed
   - searchable profile database
   - tracking and signal configuration
```

### Data model

| Table | Purpose |
|---|---|
| `companies` | Canonical company records, referenced by experience entries to avoid free-text duplication |
| `people` | One row per tracked individual, including current status and signal flags |
| `experience` | Work history entries, linking people to companies over time |
| `alerts` | A log of every detected status transition, including a confidence score |
| `signal_preferences` | User-defined tracking criteria, such as target companies or status types |

## Current state

This repository is a proof-of-concept frontend and data model, built to validate the product concept before investing in live data infrastructure. It is not yet connected to a real data source.

| Component | Status |
|---|---|
| Database schema | Implemented |
| Frontend (alert feed, profile browser, insights, scan settings) | Implemented |
| Dummy data layer | Implemented |
| Live LinkedIn data ingestion | Not implemented |
| Automated classification (LLM-based labeling) | Not implemented |
| Scheduled scanning / change detection | Not implemented |

All profiles, companies, and alerts currently in the database are fictional and were generated for demonstration purposes.

## Why a confidence score, not a binary signal

Not all status changes are equally meaningful. Someone leaving a company is a weak signal on its own; someone leaving a company for the second time after previously founding and exiting a startup is a much stronger one. Rather than treating every detected change identically, each alert carries a confidence score reflecting how likely it is to represent genuine founding intent, based on factors such as repeat-founder history, seniority, and tenure patterns. In the current proof of concept, these scores are illustrative and manually assigned; in a production version, this would be the primary candidate for a learned or rules-based model.

## Tech stack

- **Frontend:** Streamlit
- **Database:** Supabase (PostgreSQL)
- **Visualization:** Plotly
- **Data layer (planned):** Third-party LinkedIn data API
- **Classification layer (planned):** LLM-based profile labeling

## Known limitations

This proof of concept intentionally does not address several open problems that a production version would need to solve:

- **Signal frequency.** Senior, high-quality operators change roles infrequently. Even at meaningful scale, the expected rate of relevant status changes per week is low. Any production version needs either a wider tracked population, additional signal sources beyond LinkedIn, or a narrower, higher-yield tracked list to be useful at the cadence investors expect.
- **Data sourcing.** Live LinkedIn data acquisition carries real legal and platform-policy considerations that have not been resolved in this proof of concept and would need review before any live data source is connected.
- **Classification accuracy.** Status classification (employed, stealth, founder) has edge cases, such as profiles that are simply outdated rather than reflecting a genuine change, that require either careful prompt design or human review to handle reliably.
