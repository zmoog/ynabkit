import dataclasses
import datetime


@dataclasses.dataclass
class Transaction:
    id: str
    name: str
    state: str
    kind: str
    date: datetime.datetime
    amount: float
    currency: str
    extra_info: str
    