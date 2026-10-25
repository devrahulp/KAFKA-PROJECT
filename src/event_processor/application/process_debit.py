from event_processor.application.ports import DebitStore
from event_processor.domain.events import DebitRequested


class ProcessDebit:
    def __init__(self, debit_store: DebitStore) -> None:
        self._debit_store = debit_store

    def handle(self, event: DebitRequested) -> bool:
        return self._debit_store.debit_once(event)
