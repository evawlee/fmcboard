import pytest

from fmcboard.audit_log import AuditLog, AuditToken, AuditScopeError
from fmcboard.policy_engine import PolicyEngine
from fmcboard.bundle_loader import PolicyBundle
from fmcboard.telemetry_pipeline import TelemetryEvent
from fmcboard.wire_codec import encode_envelope, decode_envelope
from fmcboard.tenant_context import TenantContext
from fmcboard.policy_schema import PolicyAction, PolicyMetadata
from fmcboard.policy_wire import PolicyWireBuilder, WireEncodingError


_WRITE_TOKEN = AuditToken(operator="alex", scopes=("audit:read", "audit:write"))


def _bundle_blob(bid, version=1):
    return (
        '{"metadata": {"bundle_id": "' + bid + '", "tenant_id": "t-1", "version": '
        + str(version) + '}, "actions": [{"rule_id": "r-1", "action": "allow", "priority": 10}]}'
    ).encode("utf-8")


def _baseline_payload():
    return {
        "rule_id": "r-001",
        "action": "allow",
        "target_device": "ftd-edge-1",
        "operator_note": "approved by alex",
    }


class TestPolicyWireBuilderLegitimate:
    def test_encode_returns_bytes(self):
        builder = PolicyWireBuilder(fleet_tag="fleet-east")
        result = builder.encode_for_ftd(_baseline_payload())
        assert isinstance(result, bytes)

    def test_encode_includes_rule_id_field(self):
        builder = PolicyWireBuilder(fleet_tag="fleet-east")
        result = builder.encode_for_ftd(_baseline_payload())
        assert b"rule_id=r-001" in result

    def test_encode_includes_action_field(self):
        builder = PolicyWireBuilder(fleet_tag="fleet-east")
        result = builder.encode_for_ftd(_baseline_payload())
        assert b"action=allow" in result

    def test_encode_includes_target_field(self):
        builder = PolicyWireBuilder(fleet_tag="fleet-east")
        result = builder.encode_for_ftd(_baseline_payload())
        assert b"target=ftd-edge-1" in result

    def test_two_encoders_independent_fleet_tag(self):
        a = PolicyWireBuilder(fleet_tag="fleet-east")
        b = PolicyWireBuilder(fleet_tag="fleet-west")
        out_a = a.encode_for_ftd(_baseline_payload())
        out_b = b.encode_for_ftd(_baseline_payload())
        assert b"fleet=fleet-east" in out_a
        assert b"fleet=fleet-west" in out_b


class TestAuditLogLegitimate:
    def test_record_deploy_with_write_scope_appended(self):
        log = AuditLog()
        log.record_deploy(_WRITE_TOKEN, "ftd-edge-1", {"bundle_id": "b-1"})
        assert len(log.entries()) == 1
        assert log.entries()[0].method == "deploy"

    def test_record_rollback_with_write_scope_appended(self):
        log = AuditLog()
        log.record_rollback(_WRITE_TOKEN, "ftd-edge-1", {"bundle_id": "b-1"})
        assert log.entries()[0].method == "rollback"

    def test_record_revoke_with_write_scope_appended(self):
        log = AuditLog()
        log.record_revoke(_WRITE_TOKEN, "ftd-edge-1", {"bundle_id": "b-1"})
        assert log.entries()[0].method == "revoke"

    def test_record_chain_preserves_order(self):
        log = AuditLog()
        log.record_deploy(_WRITE_TOKEN, "ftd-edge-1", {"bundle_id": "b-1"})
        log.record_rollback(_WRITE_TOKEN, "ftd-edge-1", {"bundle_id": "b-1"})
        log.record_revoke(_WRITE_TOKEN, "ftd-edge-1", {"bundle_id": "b-1"})
        methods = [r.method for r in log.entries()]
        assert methods == ["deploy", "rollback", "revoke"]

    def test_record_includes_operator_from_token(self):
        log = AuditLog()
        log.record_deploy(_WRITE_TOKEN, "ftd-edge-1", {"bundle_id": "b-1"})
        assert log.entries()[0].operator == "alex"


class TestPolicyEngineLegitimate:
    def test_register_and_lookup_bundle(self):
        engine = PolicyEngine(tenant_id="tenant-alpha")
        bundle = PolicyBundle.load(_bundle_blob("b-1"))
        engine.register_bundle("b-1", bundle)
        assert engine.has_bundle("b-1")
        assert engine.lookup_bundle("b-1").metadata.bundle_id == "b-1"

    def test_subscribe_then_lookup_subscribers(self):
        engine = PolicyEngine(tenant_id="tenant-alpha")
        engine.subscribe("baseline_route_advert", "edge-1")
        engine.subscribe("baseline_route_advert", "edge-2")
        assert engine.subscribers_for("baseline_route_advert") == {"edge-1", "edge-2"}

    def test_unsubscribe_removes_subscriber(self):
        engine = PolicyEngine(tenant_id="tenant-alpha")
        engine.subscribe("baseline_link_state", "edge-1")
        engine.unsubscribe("baseline_link_state", "edge-1")
        assert engine.subscribers_for("baseline_link_state") == set()


class TestBundleLoader:
    def test_load_round_trip(self):
        bundle = PolicyBundle.load(_bundle_blob("b-1", version=3))
        assert bundle.metadata.bundle_id == "b-1"
        assert bundle.metadata.version == 3
        assert bundle.actions[0].action == "allow"

    def test_load_rejects_malformed_json(self):
        with pytest.raises(Exception):
            PolicyBundle.load(b"not-json")


class TestTelemetryPipeline:
    def test_from_wire_round_trip(self):
        blob = b'{"event_kind": "route_update", "tenant_id": "t-1", "payload": {"route": "0.0.0.0/0"}}'
        event = TelemetryEvent.from_wire(blob)
        assert event.event_kind == "route_update"
        assert event.payload["route"] == "0.0.0.0/0"

    def test_from_wire_empty_payload(self):
        blob = b'{"event_kind": "heartbeat", "tenant_id": "t-1"}'
        event = TelemetryEvent.from_wire(blob)
        assert event.payload == {}


class TestWireCodec:
    def test_encode_decode_round_trip(self):
        payload = {"k": "v", "n": 42}
        assert decode_envelope(encode_envelope(payload)) == payload

    def test_decode_rejects_non_bytes(self):
        with pytest.raises(TypeError):
            decode_envelope("not-bytes")


class TestTenantContext:
    def test_context_carries_tenant_id(self):
        ctx = TenantContext(tenant_id="tenant-gamma", actor="alex@org", request_id="req-1")
        assert ctx.tenant_id == "tenant-gamma"
        assert ctx.region == "us-west-2"
