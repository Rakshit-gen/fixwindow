# fixwindow

An SLA clock for maintenance requests, sized for landlords with a handful
of units, not a portfolio.

## The problem

A landlord with 3-15 units runs maintenance over text messages and memory.
A tenant reports no hot water, the landlord means to call a plumber that
day, three days pass, and now it's a habitability complaint instead of a
quick fix. The tools that solve this properly (AppFolio, Buildium) are
built and priced for portfolios of dozens to hundreds of units with a
property-management company running them — a per-unit fee and an
onboarding process that doesn't make sense for someone self-managing a
duplex and a triplex.

`fixwindow` is just the part that actually prevents the bad outcome: every
request gets a category-based SLA clock the moment it's logged, the
dashboard tells you which ones are about to breach before they do, and it
keeps a record of which vendor actually shows up on time so you know who
to call next time.

## How it works

1. Log a maintenance request against a unit, with a category: emergency
   (no heat, flooding, gas leak), urgent (no hot water, broken lock), or
   routine (cosmetic).
2. Each category carries an SLA: 4 hours for emergencies, 24 for urgent,
   120 (5 business days) for routine.
3. Every open request's remaining time is computed live: on track, at
   risk (past 75% of its SLA window), or breached.
4. Once a vendor is assigned and the request is resolved, it rolls into
   that vendor's scorecard: average response time, average resolution
   time, and breach rate, so you have data instead of a gut feeling the
   next time you need a plumber.

## Stack

- **Backend**: Django + Django REST Framework, SQLite for local/demo use.
- **Frontend**: React + Vite, calling the DRF API directly.

## Running locally

```bash
# backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

# frontend
cd frontend
npm install
npm run dev
```

## What's not built

No SMS/email notifications when a request approaches breach — the
dashboard is the alert surface. No tenant-facing portal; requests are
logged by whoever's managing the properties, not self-service.
