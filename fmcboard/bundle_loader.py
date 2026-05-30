import json
from dataclasses import dataclass
from typing import Any, Dict, List

from fmcboard.policy_schema import PolicyAction, PolicyMetadata


@dataclass(frozen=True)
class PolicyBundle:
    metadata: PolicyMetadata
    actions: List[PolicyAction]

    @classmethod
    def load(cls, blob: bytes) -> "PolicyBundle":
        payload: Dict[str, Any] = json.loads(blob.decode("utf-8"))
        meta = PolicyMetadata(
            bundle_id=str(payload["metadata"]["bundle_id"]),
            tenant_id=str(payload["metadata"]["tenant_id"]),
            version=int(payload["metadata"]["version"]),
        )
        actions = [
            PolicyAction(
                rule_id=str(a["rule_id"]),
                action=str(a["action"]),
                priority=int(a["priority"]),
            )
            for a in payload.get("actions", [])
        ]
        return cls(metadata=meta, actions=actions)
