# OCI Managed Postgres CPU-Memory Spikes and Rabbit Backlog Avalanche

## Overview

An incident where an **OCI managed Postgres** backend becomes unstable under load (CPU/memory spikes and intermittent unavailability), while a Kubernetes application (**connect**) continues to retry and/or consume messages from **RabbitMQ**, creating an **avalanche effect**: backlog grows, reconnections surge, and the database flaps even harder.

In practice, the fastest path to recovery is almost always:

1. **Stop the source of pressure** (pause consumers / scale down connect),
2. **Let the database stabilize**,
3. **Remove/contain backlog triggers** (purge or isolate the queue),
4. **Fix inconsistent “stuck” data states** (via SQL),
5. **Ramp up the app gradually** to avoid re-triggering the avalanche.

---

## Symptoms

- OCI Postgres shows **CPU and memory spikes** and becomes intermittently unavailable.
- Application pods restart or stall, often with connection/pool errors.
- RabbitMQ queue (e.g., invoices/billing) grows quickly; retries increase publish/consume churn.
- Each app restart makes things worse: when connect comes back, it “picks everything at once” and the system collapses again.

---

## Common Indicators (what you typically see)

### In the app (Kubernetes / Lens)

- Pods are healthy from Kubernetes’ perspective but **latency/timeouts** explode.
- Pool saturation patterns: lots of concurrent DB connections, slow queries, request timeouts, elevated error rate.
- Restarts can happen if the app runs out of memory or has aggressive liveness/readiness checks.

### In RabbitMQ (UI)

- A specific queue is the main driver (e.g., “invoices”).
- **Backlog increases** and does not drain; publish spikes; consumers may churn.

### In Postgres (DBeaver)

- Connections climb (sometimes rapidly) as app retries.
- `pg_stat_activity` shows many sessions from the app, often waiting or timing out.
- Queries that are normally fast become slow due to CPU pressure / IO contention / lock contention.

---

## Root Cause and Context (most common pattern)

This class of incident often involves **multiple reinforcing loops**:

- **Retry storm**: connect (or its workers) retries aggressively on DB errors, increasing connection churn.
- **Backlog avalanche**: Rabbit backlog + “catch-up” behavior causes a burst of work when the app returns.
- **Connection pool behavior**: pool size × replicas × workers becomes “too many connections”, pushing the managed DB past stability.
- **No ramp-up / no backpressure**: when the app restarts, it resumes full consumption instantly.

Important: in **managed** Postgres you rarely “fix” the DB by manipulating the process directly; you fix it by **removing pressure** and waiting for the service to stabilize.

---

## Solution (what worked in practice)

### 1) Contain: stop pressure from connect

Goal: stop new connections and stop consuming/publishing invoice messages.

Typical action:

- Scale **connect workers/consumers** down (often to zero) so the DB can recover.
- If API and worker are separate, stop **only the worker** first to keep the API available.

### 2) Wait for the database to stabilize

Goal: restore a stable baseline before reintroducing load.

Validation via DBeaver:

- Confirm you can connect consistently.
- Run only light checks initially (avoid expensive queries).

### 3) Remove the backlog trigger in RabbitMQ

Goal: prevent the “catch-up burst” from bringing the DB down again.

Typical action:

- Purge the problematic queue (fastest) **or**
- Move messages to a DLQ/quarantine flow if available (safer, slower operationally).

### 4) Fix “stuck” invoice states in Postgres

Goal: remove inconsistent states that keep re-triggering retries and reprocessing loops.

Typical action (SQL):

- Identify invoices stuck in “PROCESSING” / “SENT” / “GENERATING” past a threshold.
- Either reset them for a controlled reprocess later, or mark them as “ERROR” for manual triage.

This is commonly the “I saved what I could; the rest was dropped/reset” part of the incident.

### 5) Bring connect back with ramp-up

Goal: avoid another avalanche.

Typical action:

- Start with minimal capacity (few replicas).
- Watch DB connections, queue depth, and app error rate.
- Increase replicas gradually only after the system is draining backlog and latency is stable.

---

## Safe Simulation (to practice without breaking prod)

You cannot (and should not) try to force a managed Postgres process crash. Instead, simulate the **same effect on the app**:

### Simulation A: DB unavailability from the app’s perspective

- Temporarily block or degrade connect → Postgres traffic (latency, loss, disconnects).
- Observe:
  - pool exhaustion patterns,
  - retry behavior,
  - queue growth,
  - recovery behavior when the network is restored.

### Simulation B: Backlog avalanche

- Pre-fill a test queue with many “invoice” messages.
- Bring consumers up without ramp-up and watch the catch-up burst.
- Repeat with ramp-up and/or backpressure enabled; compare outcomes.

### What “success” looks like in a drill

- You can contain quickly (stop consumers first).
- The DB stabilizes without prolonged flapping.
- You can prevent re-triggering (queue isolation/purge/quarantine).
- You can recover with gradual ramp-up, keeping latency and error rates within bounds.

---

## Mitigation (prevent this class of incident)

- **Backpressure / ramp-up**: consumers should start gradually and respect a max in-flight.
- **Retry discipline**: exponential backoff + jitter; avoid synchronized retries.
- **Connection limits**: pool size must be bounded per pod; total connections must fit the managed DB capacity.
- **Queue hygiene**: DLQ/quarantine path for poison messages; avoid infinite requeue loops.
- **Operational runbook**: “pause consumers → stabilize DB → isolate backlog → fix stuck states → ramp-up”.

---

## Resolved as

Incident mitigated by **stopping connect to remove pressure**, allowing the **managed Postgres** to stabilize, then **purging the invoice queue** to prevent backlog avalanche, followed by **resetting/adjusting stuck invoice statuses** and **bringing connect back gradually**.

