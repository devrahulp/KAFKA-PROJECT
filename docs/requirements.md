# Fault-Tolerant Event Processing System — SRS 1

## Goal
Process account-debit events from Kafka and apply each event to PostgreSQL at most once, even if Kafka redelivers it after a worker failure.

This project simulates account balances locally. It does not connect to a real payment provider.

## Event
Each debit event contains:
- event_id: unique identifier for this event
- event_type: account.debit.requested
- schema_version: 1
- account_id: account to debit
- amount_cents: positive whole number of cents

The Kafka message key is account_id so events for the same account are routed to the same partition.

## Processing rules
1. A worker reads an event from Kafka.
2. In one PostgreSQL transaction, it records the event_id, debits the account, and records a ledger entry.
3. If the event_id was already processed, it skips the debit.
4. The worker commits the Kafka offset only after the PostgreSQL transaction succeeds.

## Failure behavior
- If the worker fails before the database transaction commits, PostgreSQL rolls back the transaction. Kafka can deliver the event again.
- If the worker fails after the database transaction commits but before the Kafka offset commits, Kafka can deliver the event again. The existing event_id prevents a second debit.
- Retry topics, a dead-letter queue, replay, metrics, and load testing are later increments.

## SRS 1 acceptance criteria
- A valid new event reduces the account balance by amount_cents.
- Processing the same event_id again does not reduce the balance again.
- A debit and its event/ledger records commit together or roll back together.
- The Kafka offset is committed only after the database transaction succeeds.
