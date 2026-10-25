from typing import Protocol

from event_processor.domain.events import DebitRequested


class DebitStore(Protocol):
    def debit_once(self, event: DebitRequested) -> bool:
        """Apply the debit once; return False if this event was already handled."""
