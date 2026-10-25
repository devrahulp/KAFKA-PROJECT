from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DebitRequested(BaseModel):
    """A request to debit an account, represented in whole cents."""

    model_config = ConfigDict(extra="forbid")

    event_id: UUID
    event_type: Literal["account.debit.requested"]
    schema_version: Literal[1]
    occurred_at: datetime
    account_id: str = Field(min_length=1)
    amount_cents: int = Field(gt=0)