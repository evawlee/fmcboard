from dataclasses import dataclass


@dataclass(frozen=True)
class PolicyAction:
    rule_id: str
    action: str
    priority: int


@dataclass(frozen=True)
class PolicyMetadata:
    bundle_id: str
    tenant_id: str
    version: int
