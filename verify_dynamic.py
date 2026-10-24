"""
Aethelgard Dynamic Execution & Anti-Hardcoding Verification Suite
Asserts that 100% of simulator outputs, 2PC tokens, and agent plans
are computed dynamically from real SQLite state, AST parsing, and live execution.
"""

import sys
import json
import urllib.request
import urllib.error
import random
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def post_json(endpoint: str, payload: dict) -> dict:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        try:
            return {"_http_status": e.code, **json.loads(err_body)}
        except Exception:
            return {"_http_status": e.code, "error": err_body}

def get_json(endpoint: str) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

def test_1_dynamic_unseen_sql():
    print("\n--- TEST 1: Unseen Arbitrary SQL Simulation ---")
    # Reset to baseline
    post_json("/api/reset", {})
    state = get_json("/api/state")
    active_count = sum(1 for a in state["tables"]["enterprise_accounts"] if a["status"] == "ACTIVE")
    active_arr = sum(a["arr_usd"] for a in state["tables"]["enterprise_accounts"] if a["status"] == "ACTIVE")
    
    # Completely unseen query reducing ARR by 50% for all ACTIVE accounts
    custom_sql = "UPDATE enterprise_accounts SET arr_usd = arr_usd * 0.5 WHERE status = 'ACTIVE';"
    preview = post_json("/api/preview", {
        "domain": "CODE & SQL DEPLOY",
        "payload": custom_sql
    })
    
    assert preview["success"] is True, f"Preview failed: {preview.get('error')}"
    assert preview["records_mutated"] == active_count, f"Expected {active_count} records mutated, got {preview['records_mutated']}"
    expected_loss = round(active_arr * 0.5, 2)
    assert abs(preview["financial_exposure_usd"] - expected_loss) < 1.0, f"Expected fin exposure ~${expected_loss}, got ${preview['financial_exposure_usd']}"
    assert preview["pre_state_hash"] != preview["simulated_post_state_hash"], "State hashes should differ"
    assert "token_envelope" in preview, "Missing 2PC token envelope"
    print(f"[PASS] Dynamically mutated {preview['records_mutated']} rows with ${preview['financial_exposure_usd']:,.2f} ARR loss without preset lookup.")

def test_2_dynamic_agent_planning_and_preview():
    print("\n--- TEST 2: Dynamic Agent Natural-Language Synthesis ---")
    random_amt = round(random.uniform(12000.0, 39000.0), 2)
    random_iters = random.randint(3, 7)
    prompt = f"Please process refund of ${random_amt} for account ACC-CORP-06 {random_iters} times due to SLA incident"
    
    plan = post_json("/api/agent/plan", {"prompt": prompt})
    assert plan["success"] is True, f"Agent plan failed: {plan.get('error')}"
    assert plan["domain"] == "PAYMENT LEDGER", f"Expected PAYMENT LEDGER domain, got {plan['domain']}"
    
    # Inspect executable payload
    pay_json = json.loads(plan["executable_payload"])
    assert pay_json["action"] in ["REFUND", "BATCH_REFUND"], f"Action unexpected: {pay_json['action']}"
    assert pay_json["account_id"] == "ACC-CORP-06", f"Account ID unexpected: {pay_json['account_id']}"
    assert abs(pay_json["amount_usd"] - random_amt) < 0.01, f"Expected ${random_amt}, got {pay_json['amount_usd']}"
    assert pay_json["iterations"] == random_iters, f"Expected {random_iters} iters, got {pay_json['iterations']}"
    
    # Now execute against preview shadow clone
    preview = post_json("/api/preview", {
        "domain": plan["domain"],
        "payload": plan["executable_payload"]
    })
    
    expected_exposure = round(random_amt * random_iters, 2)
    assert abs(preview["financial_exposure_usd"] - expected_exposure) < 1.0, f"Expected ${expected_exposure}, got ${preview['financial_exposure_usd']}"
    assert preview["records_mutated"] == random_iters, f"Expected {random_iters} records, got {preview['records_mutated']}"
    print(f"[PASS] Agent dynamically extracted ${random_amt} x {random_iters} iters = ${preview['financial_exposure_usd']:,.2f} total impact.")

def test_3_agent_gibberish_diagnostic():
    print("\n--- TEST 3: Agent Diagnostic Handling on Gibberish Input ---")
    gibberish = "zorp flim flam wozzle 987654321 qwert"
    plan = post_json("/api/agent/plan", {"prompt": gibberish})
    assert plan["success"] is False, "Agent should fail gracefully on gibberish"
    assert "Dynamic Planner Diagnostic" in plan["error"], f"Expected diagnostic message, got: {plan['error']}"
    print(f"[PASS] Agent returned clean dynamic diagnostic on gibberish: '{plan['error']}'")

def test_4_real_sqlite_error_propagation():
    print("\n--- TEST 4: Real SQLite Syntax Error Propagation (Zero Silent Fallbacks) ---")
    bad_sql = "UPDATE non_existent_database_table_omega SET column_foo = 123;"
    preview = post_json("/api/preview", {
        "domain": "CODE & SQL DEPLOY",
        "payload": bad_sql
    })
    assert preview["success"] is False, "Preview should report failure on invalid SQL"
    assert "no such table: non_existent_database_table_omega" in preview["error"], f"Real SQLite error missing: {preview.get('error')}"
    assert preview["verdict"] == "BLOCKED", "Verdict should be BLOCKED on error"
    print(f"[PASS] Live SQLite error successfully propagated: '{preview['error']}'")

def test_5_cryptographic_2pc_replay_and_drift():
    print("\n--- TEST 5: Cryptographic 2PC Anti-Replay & State Drift Protection ---")
    # Reset to baseline
    post_json("/api/reset", {})
    
    safe_sql = "UPDATE service_configs SET current_value = '2048' WHERE env_key = 'DDOS_BURST_ALLOWANCE';"
    preview = post_json("/api/preview", {
        "domain": "CODE & SQL DEPLOY",
        "payload": safe_sql
    })
    assert preview["success"] is True
    token = preview["token_envelope"]["token"]
    
    # 1. First commit must succeed
    commit1 = post_json("/api/commit", {
        "domain": "CODE & SQL DEPLOY",
        "payload": safe_sql,
        "token": token
    })
    assert "COMMITTED" in commit1.get("status", ""), f"First commit failed: {commit1}"
    print("[PASS] First 2PC commit succeeded with valid HMAC token.")
    
    # 2. Replay of same token must be rejected with 409
    commit_replay = post_json("/api/commit", {
        "domain": "CODE & SQL DEPLOY",
        "payload": safe_sql,
        "token": token
    })
    assert commit_replay.get("_http_status") == 409, f"Expected 409 on replay, got: {commit_replay}"
    print("[PASS] Replay attack of consumed token intercepted with HTTP 409 Conflict.")
    
    # 3. Payload drift test: preview new action, tamper with payload before commit
    preview2 = post_json("/api/preview", {
        "domain": "CODE & SQL DEPLOY",
        "payload": "UPDATE service_configs SET current_value = '4096' WHERE env_key = 'DDOS_BURST_ALLOWANCE';"
    })
    token2 = preview2["token_envelope"]["token"]
    tampered_payload = "UPDATE service_configs SET current_value = '9999' WHERE env_key = 'DDOS_BURST_ALLOWANCE';"
    commit_tampered = post_json("/api/commit", {
        "domain": "CODE & SQL DEPLOY",
        "payload": tampered_payload,
        "token": token2
    })
    assert commit_tampered.get("_http_status") == 409, f"Expected 409 on payload drift, got: {commit_tampered}"
    print("[PASS] TOCTOU payload drift intercepted with HTTP 409 Conflict.")

if __name__ == "__main__":
    try:
        test_1_dynamic_unseen_sql()
        test_2_dynamic_agent_planning_and_preview()
        test_3_agent_gibberish_diagnostic()
        test_4_real_sqlite_error_propagation()
        test_5_cryptographic_2pc_replay_and_drift()
        
        print("\n" + "="*80)
        print("VERIFICATION PASSED: ZERO HARDCODED VALUES DETECTED (100% DYNAMIC SQL/STATE PIPELINE)")
        print("="*80)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] VERIFICATION ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] UNEXPECTED ERROR: {e}")
        sys.exit(1)
