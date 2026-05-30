# fmcboard

Security telemetry aggregator with multi-tenant policy push. Tenants upload
serialized policy bundles and emit telemetry events; a central policy
engine tracks loaded bundles and per-event-kind subscribers.

## Layout

- `fmcboard/policy_schema.py` - PolicyAction dataclass
- `fmcboard/bundle_loader.py` - PolicyBundle.load(blob) inbound bundles
- `fmcboard/telemetry_pipeline.py` - TelemetryEvent.from_wire(blob) inbound events
- `fmcboard/policy_engine.py` - PolicyEngine per-tenant state
- `fmcboard/tenant_context.py` - TenantContext + token parsing
- `fmcboard/audit_log.py` - in-memory audit
- `fmcboard/wire_codec.py` - envelope helpers used on trusted payloads

## Tests

```
pip install -e .
pytest tests/
```
