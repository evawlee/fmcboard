import json
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class TelemetryEvent:
    event_kind: str
    tenant_id: str
    payload: Dict[str, Any]

    @classmethod
    def from_wire(cls, blob: bytes) -> "TelemetryEvent":
        record: Dict[str, Any] = json.loads(blob.decode("utf-8"))
        return cls(
            event_kind=str(record["event_kind"]),
            tenant_id=str(record["tenant_id"]),
            payload=dict(record.get("payload", {})),
        )
