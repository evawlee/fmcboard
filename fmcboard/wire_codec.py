import json
from typing import Any


def encode_envelope(payload: Any) -> bytes:
    return json.dumps(payload, sort_keys=True).encode("utf-8")


def decode_envelope(blob: bytes) -> Any:
    if not isinstance(blob, (bytes, bytearray)):
        raise TypeError("blob must be bytes")
    return json.loads(blob.decode("utf-8"))
