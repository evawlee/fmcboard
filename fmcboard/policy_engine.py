from typing import Dict, Set, List
from .bundle_loader import PolicyBundle

class PolicyEngine:
    _loaded_bundles: Dict[str, PolicyBundle] = {}
    _active_subscribers: Dict[str, Set[str]] = {}

    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id

    def register_bundle(self, bundle_id: str, bundle: PolicyBundle) -> None:
        self._loaded_bundles[bundle_id] = bundle

    def lookup_bundle(self, bundle_id: str) -> PolicyBundle:
        return self._loaded_bundles[bundle_id]

    def has_bundle(self, bundle_id: str) -> bool:
        return bundle_id in self._loaded_bundles

    def list_loaded_bundle_ids(self) -> List[str]:
        return list(self._loaded_bundles.keys())

    def subscribe(self, event_kind: str, subscriber_id: str) -> None:
        if event_kind not in self._active_subscribers:
            self._active_subscribers[event_kind] = set()
        self._active_subscribers[event_kind].add(subscriber_id)

    def unsubscribe(self, event_kind: str, subscriber_id: str) -> None:
        if event_kind in self._active_subscribers:
            self._active_subscribers[event_kind].discard(subscriber_id)

    def subscribers_for(self, event_kind: str) -> Set[str]:
        return set(self._active_subscribers.get(event_kind, set()))

    def list_event_kinds(self) -> List[str]:
        return list(self._active_subscribers.keys())
