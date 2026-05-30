from typing import Mapping


class WireEncodingError(Exception):
    pass


class PolicyWireBuilder:
    def __init__(self, fleet_tag: str = "default"):
        self.fleet_tag = fleet_tag

    def encode_for_ftd(self, payload: Mapping[str, str]) -> bytes:
        rule_id = payload.get("rule_id", "")
        action = payload.get("action", "")
        target_device = payload.get("target_device", "")
        operator_note = payload.get("operator_note", "")
        parts = [
            f"fleet={self.fleet_tag}",
            f"rule_id={rule_id}",
            f"action={action}",
            f"target={target_device}",
            f"note={operator_note}",
        ]
        frame = ";".join(parts)
        return frame.encode("utf-8")
