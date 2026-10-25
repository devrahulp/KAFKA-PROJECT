from psycopg import connect
from psycopg.types.json import Jsonb

from event_processor.domain.events import DebitRequested
from event_processor.settings import settings


class DebitRejected(Exception):
    """The account is missing or does not have enough funds."""


class PostgresDebitRepository:
    def debit_once(self, event: DebitRequested) -> bool:
        with connect(settings.database_url) as conn:
            claimed = conn.execute(
                """
                INSERT INTO processed_events
                    (event_id, event_type, schema_version, payload)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (event_id) DO NOTHING
                RETURNING event_id
                """,
                (
                    event.event_id,
                    event.event_type,
                    event.schema_version,
                    Jsonb(event.model_dump(mode="json")),
                ),
            ).fetchone()

            if claimed is None:
                return False

            debited = conn.execute(
                """
                UPDATE accounts
                SET balance_cents = balance_cents - %s
                WHERE account_id = %s AND balance_cents >= %s
                RETURNING account_id
                """,
                (event.amount_cents, event.account_id, event.amount_cents),
            ).fetchone()

            if debited is None:
                raise DebitRejected(
                    f"Account {event.account_id!r} is missing or has insufficient funds"
                )

            conn.execute(
                """
                INSERT INTO debit_ledger (event_id, account_id, amount_cents)
                VALUES (%s, %s, %s)
                """,
                (event.event_id, event.account_id, event.amount_cents),
            )

        return True
