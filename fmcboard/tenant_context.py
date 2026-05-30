from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    actor: str
    request_id: str
    region: str = 'us-west-2'

    def is_admin(self) -> bool:
        return self.actor.startswith('admin@')

def context_from_token(token: str) -> Optional[TenantContext]:
    if not isinstance(token, str) or not token:
        return None
    parts = token.split('|')
    if len(parts) < 3 or len(parts) > 4:
        return None
    if any((not p for p in parts[:3])):
        return None
    region = parts[3] if len(parts) == 4 else 'us-west-2'
    return TenantContext(tenant_id=parts[0], actor=parts[1], request_id=parts[2], region=region)
