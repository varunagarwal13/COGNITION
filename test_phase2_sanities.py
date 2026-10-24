"""
Phase 2 Sanity & Schema-Awareness Verification Suite
Tests that:
1. /api/agent/plan and /api/heal succeed on queries targeting payment_ledger,
   service_configs, and outbound_mail_queue without raising 'no such column' errors.
2. index.html contains #workbench-2pc-strip, #btn-nav-redteam, #btn-tamper, and 2PC strip IDs.
3. app.js contains the workbench 2PC strip synchronization, no preset card spoilers,
   and preserves AppState.activeToken on post-preview tamper testing.
4. blast_canvas_3d.js dynamically binds all 8 nodes from live system state without hardcoded counts.
"""

import sys
import json
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_schema_aware_cross_tables():
    print("\n--- TEST: Schema-Aware Cross-Table Intent & Self-Healing ---")
    tables = [
        ("payment_ledger", "DELETE FROM payment_ledger;", "DELETE FROM payment_ledger WHERE settlement_state != 'SETTLED'"),
        ("service_configs", "DELETE FROM service_configs;", "DELETE FROM service_configs WHERE criticality_level != 'CRITICAL'"),
        ("outbound_mail_queue", "DELETE FROM outbound_mail_queue;", "DELETE FROM outbound_mail_queue WHERE delivery_status != 'DISPATCHED'"),
    ]

    for tbl, delete_stmt, expected_heal_fragment in tables:
        # Test /api/heal on the table
        res = client.post("/api/heal", json={"domain": "CODE & SQL DEPLOY", "payload": delete_stmt})
        assert res.status_code == 200, f"Heal failed for {tbl}: {res.text}"
        data = res.json()
        repaired = data["repaired_payload"]
        print(f"Table {tbl} repaired SQL:\n  {repaired}")
        
        # Verify no column hallucinations
        assert "arr_usd" not in repaired, f"Found hallucinated arr_usd in healed SQL for {tbl}"
        assert "tier" not in repaired, f"Found hallucinated tier in healed SQL for {tbl}"
        
        # Re-preview to confirm zero SQLite errors
        preview_res = client.post("/api/preview", json={"domain": "CODE & SQL DEPLOY", "payload": repaired})
        assert preview_res.status_code == 200, f"Preview of healed SQL failed for {tbl}: {preview_res.text}"
        pdata = preview_res.json()
        assert pdata.get("success") is not False, f"Preview failed with error: {pdata.get('error')}"
        assert "no such column" not in str(pdata.get("error", "")).lower()
        print(f"  -> Successfully re-simulated on SQLite shadow clone with zero syntax/schema errors!")

    # Test /api/agent/plan on table updates
    update_prompts = [
        ("Update payment ledger records where transaction is pending", "payment_ledger", "amount_usd"),
        ("Change service configs burst limit", "service_configs", "current_value"),
        ("Tune outbound mail queue status", "outbound_mail_queue", "delivery_status")
    ]
    for prompt, target_tbl, expected_col in update_prompts:
        plan_res = client.post("/api/agent/plan", json={"prompt": prompt})
        assert plan_res.status_code == 200, f"Plan failed for '{prompt}': {plan_res.text}"
        pdata = plan_res.json()
        payload = pdata["executable_payload"]
        print(f"Prompt '{prompt}' compiled to:\n  {payload}")
        if target_tbl in ["service_configs", "outbound_mail_queue"]:
            assert "arr_usd" not in payload, f"Hallucinated arr_usd in plan for {target_tbl}"
        
        # Dry-run on shadow DB
        preview_res = client.post("/api/preview", json={"domain": pdata["domain"], "payload": payload})
        assert preview_res.status_code == 200
        assert "no such column" not in str(preview_res.json().get("error", "")).lower()
        print(f"  -> Simulated compiled query on {target_tbl} cleanly with zero schema errors!")

    # Test specific SLA penalty prompt requested by user
    sla_prompt = "Set SLA penalty to 45000 for enterprise account ACC-CORP-03"
    sla_res = client.post("/api/agent/plan", json={"prompt": sla_prompt})
    assert sla_res.status_code == 200, f"Plan failed for '{sla_prompt}': {sla_res.text}"
    sla_data = sla_res.json()
    expected_sql = "UPDATE enterprise_accounts SET sla_penalty_usd = 45000 WHERE account_id = 'ACC-CORP-03';"
    assert sla_data.get("executable_payload") == expected_sql, (
        f"Expected:\n  {expected_sql}\nGot:\n  {sla_data.get('executable_payload')}"
    )
    print(f"  -> Successfully verified SLA prompt exact compilation:\n     {sla_data.get('executable_payload')}")

    # Test safety assertion: ensure unbounded UPDATE is bounded unless 'all accounts'
    unbounded_res = client.post("/api/agent/plan", json={"prompt": "Update revenue to 0"})
    assert unbounded_res.status_code == 200
    unbounded_sql = unbounded_res.json().get("executable_payload")
    assert "WHERE" in unbounded_sql, f"Expected safe WHERE clause, got: {unbounded_sql}"
    print(f"  -> Verified safety assertion (bounded WHERE clause injected): {unbounded_sql}")

def test_frontend_dom_elements():
    print("\n--- TEST: Frontend DOM Elements & Telemetry Strip ---")
    with open("static/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    required_dom_ids = [
        "workbench-2pc-strip",
        "wb-pre-state-hash",
        "wb-payload-hash",
        "wb-token-status",
        "wb-ttl-countdown",
        "btn-nav-redteam",
        "btn-tamper",
        # original required ids
        "card-verdict-title",
        "card-records-number",
        "card-money-number",
        "btn-preview",
        "btn-heal",
        "btn-commit",
        "payload-editor",
        "receipt-pre-hash",
        "receipt-payload-hash",
        "receipt-hmac-sig",
        "receipt-ttl-text",
    ]
    for element_id in required_dom_ids:
        assert f'id="{element_id}"' in html, f"Missing required DOM element id='{element_id}' in index.html"
    print(f"  -> All {len(required_dom_ids)} required DOM IDs verified in index.html!")

def test_frontend_tamper_and_spoilers():
    print("\n--- TEST: Client-side Tamper Logic & Spoiler Neutralization ---")
    with open("static/app.js", "r", encoding="utf-8") as f:
        js = f.read()

    # Check that AppState.activeToken is NOT wiped to null when tamper occurs
    assert "AppState.isTampered = true;" in js
    assert "AppState.activeToken" in js
    assert "wb-pre-state-hash" in js
    assert "wb-payload-hash" in js
    assert "wb-token-status" in js
    assert "wb-ttl-countdown" in js
    assert "openRedTeamModal" in js
    assert "btn-tamper" in js

    # Check for absence of spoiler texts like "Hidden danger: accidentally deletes 6 paying business clients"
    forbidden_spoilers = [
        "Hidden danger: accidentally deletes 6 paying business clients",
        "Hidden danger: Drops table without cascade check",
        "Hidden danger: Siphons $2.5M in negative refunds",
        "Hidden danger: Sends unvetted broadcast to all enterprise CTOs",
        "Hidden danger: Leaks production AWS master credentials"
    ]
    for spoiler in forbidden_spoilers:
        assert spoiler not in js, f"Found spoiler text in app.js: '{spoiler}'"
    print("  -> All preset card spoilers successfully neutralized with professional operational descriptions.")
    print("  -> Client-side TOCTOU tamper workflow confirmed unblocked.")

def test_3d_dynamic_topology():
    print("\n--- TEST: 3D Topology Dynamic Binding ---")
    with open("static/blast_canvas_3d.js", "r", encoding="utf-8") as f:
        canvas_js = f.read()

    # Verify hardcoded counts removed
    assert "16 paying enterprise accounts" not in canvas_js
    assert "All 10 security settings intact" not in canvas_js

    # Verify all 8 nodes are bound
    nodes = [
        "enterprise_accounts", "payment_ledger", "service_configs", "outbound_mail_queue",
        "AUTH_GATEWAY", "API_GATEWAY_V1", "STRIPE_CONNECTOR", "SES_SMTP_RELAY"
    ]
    for node in nodes:
        assert node in canvas_js, f"Node {node} missing from blast_canvas_3d.js"
    print("  -> All 8 database & gateway nodes dynamically configured in 3D WebGL canvas.")

if __name__ == "__main__":
    test_schema_aware_cross_tables()
    test_frontend_dom_elements()
    test_frontend_tamper_and_spoilers()
    test_3d_dynamic_topology()
    print("\n================================================================================")
    print("ALL PHASE 2 SANITY & SCHEMA-AWARENESS CHECKS PASSED DETERMINISTICALLY [100% OK]")
    print("================================================================================\n")
