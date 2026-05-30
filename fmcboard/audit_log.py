from dataclasses import dataclass
from typing import Dict, List


class AuditScopeError(Exception):
    pass


@dataclass(frozen=True)
class AuditToken:
    operator: str
    scopes: tuple


@dataclass(frozen=True)
class AuditRecord:
    method: str
    operator: str
    target: str
    detail: Dict[str, str]


class AuditLog:
    def __init__(self):
        self._records: List[AuditRecord] = []

    def record_deploy(self, token: AuditToken, target: str, detail: Dict[str, str]) -> None:
        self._records.append(AuditRecord(method="deploy", operator=token.operator, target=target, detail=dict(detail)))

    def record_rollback(self, token: AuditToken, target: str, detail: Dict[str, str]) -> None:
        self._records.append(AuditRecord(method="rollback", operator=token.operator, target=target, detail=dict(detail)))

    def record_revoke(self, token: AuditToken, target: str, detail: Dict[str, str]) -> None:
        self._records.append(AuditRecord(method="revoke", operator=token.operator, target=target, detail=dict(detail)))

    def entries(self) -> List[AuditRecord]:
        return list(self._records)
