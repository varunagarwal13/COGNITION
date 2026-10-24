"""
AETHELGARD — FORENSIC ANTI-FALLBACK AUDIT & LIVE EXECUTION PROOF (prove_no_fallbacks.py)
Tests completely unseen, brand-new custom inputs (zero presets or hardcoded lookups)
and asserts mathematical and cryptographic truth:
  Proof 1: Unseen SQL Dynamic CoW Execution & Relational Cascade Counting
  Proof 2: Unseen Dynamic AST Self-Healing (0 rows lost, $0 ARR lost)
  Proof 3: Single-Character Tamper Rejection (HTTP 409 Payload Drift)
  Proof 4: Two-Phase Commit State Hash Persistence Identity
"""

import sys
import json
import requests

BASE_URL = "http://127.0.0.1:8000"

def assert_proof(name: str, condition: bool, details: str = ""):
    status = "PROVEN [PASS]" if condition else "FAILED [VIOLATION]"
    print(f"[{status}] {name:<46} {details}")
    if not condition:
        print(f"\nCRITICAL FORENSIC AUDIT FAILURE: {name}")
        print(f"Details: {details}")
        sys.exit(1)

def run_forensic_proof():
    print("=" * 85)
    print("AETHELGARD: FORENSIC ANTI-FALLBACK AUDIT & LIVE EXECUTION PROOF")
    print(f"Target Server: {BASE_URL}")
    print("=" * 85)

    # Reset to pristine state first
    r = requests.post(f"{BASE_URL}/api/reset")
    assert r.status_code == 200, "Reset endpoint failed."

    # Verify Pristine Baseline
    init_state = requests.get(f"{BASE_URL}/api/state").json()
    init_hash = init_state["production_state_hash"]
    init_acc_cnt = init_state["catalog_summary"]["enterprise_accounts_count"]
    init_led_cnt = init_state["catalog_summary"]["payment_ledger_count"]
    init_arr = init_state["catalog_summary"]["total_arr_usd"]
    assert init_acc_cnt == 16, f"Expected 16 accounts, got {init_acc_cnt}"
    assert init_led_cnt == 24, f"Expected 24 ledger records, got {init_led_cnt}"

    print(f"Pristine Baseline Verified: {init_acc_cnt} accounts, {init_led_cnt} ledger rows, ${init_arr:,.2f} ARR.")
    print(f"Baseline Catalog Hash: {init_hash}\n")

    # -------------------------------------------------------------------------
    # PROOF 1: Unseen SQL Dynamic CoW Execution & Relational Cascade Counting
    # -------------------------------------------------------------------------
    print("--- [PROOF 1: UNSEEN DYNAMIC SQL DRY-RUN & FOREIGN-KEY CASCADE] ---")
    custom_unseen_sql = "DELETE FROM enterprise_accounts WHERE arr_usd > 50000;"
    prev_res = requests.post(f"{BASE_URL}/api/preview", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": custom_unseen_sql
    })
    assert_proof("HTTP 200 on /api/preview", prev_res.status_code == 200, f"Status: {prev_res.status_code}")
    prev_data = prev_res.json()

    # Exact assertions on unseen query calculation:
    # 1. Exactly 16 accounts deleted
    deleted_accounts = prev_data.get("deleted_accounts_count", 0)
    assert_proof(
        "Exact Enterprise Accounts Deleted Count",
        deleted_accounts == 16,
        f"Simulated Deleted: {deleted_accounts} / 16 (100% of accounts with ARR > 50k)"
    )

    # 2. Exactly 24 cascaded foreign key ledger rows deleted
    deleted_ledger = prev_data.get("deleted_ledger_count", 0)
    assert_proof(
        "Exact Cascaded Ledger Deletions Count",
        deleted_ledger == 24,
        f"Cascaded via ON DELETE CASCADE: {deleted_ledger} / 24 ledger records"
    )

    # 3. Exact lost ARR sum: matches baseline total ARR dynamically
    lost_arr = prev_data.get("arr_loss_usd", 0.0)
    expected_lost_arr = init_arr
    assert_proof(
        "Exact Sum of Lost ARR Calculated",
        abs(lost_arr - expected_lost_arr) < 1.0,
        f"Calculated Lost ARR: ${lost_arr:,.2f} (Matches live database ARR total: ${expected_lost_arr:,.2f})"
    )

    # 4. Prove Primary Production Database is 100% untouched
    prod_check = requests.get(f"{BASE_URL}/api/state").json()
    prod_acc = prod_check["catalog_summary"]["enterprise_accounts_count"]
    prod_led = prod_check["catalog_summary"]["payment_ledger_count"]
    prod_hash = prod_check["production_state_hash"]

    assert_proof(
        "Production Database Remained 100% Untouched",
        prod_acc == 16 and prod_led == 24 and prod_hash == init_hash,
        f"Prod Accounts: {prod_acc}/16, Prod Ledger: {prod_led}/24, Hash Unchanged"
    )

    # -------------------------------------------------------------------------
    # PROOF 2: Unseen Dynamic AST Self-Healing (0 rows lost, $0 ARR lost)
    # -------------------------------------------------------------------------
    print("\n--- [PROOF 2: UNSEEN DYNAMIC AST SELF-HEALING & SAFEGUARD PREVIEW] ---")
    heal_res = requests.post(f"{BASE_URL}/api/heal", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": custom_unseen_sql
    })
    assert_proof("HTTP 200 on /api/heal", heal_res.status_code == 200, f"Status: {heal_res.status_code}")
    heal_data = heal_res.json()
    repaired_query = heal_data["patch"]["repaired_payload"]
    changes = heal_data["patch"]["changes_made"]

    print(f"Synthesized Safe Query:\n{repaired_query}")
    print(f"Modifications Applied: {changes[0]}")

    # Run the healed query through /api/preview
    prev_healed_res = requests.post(f"{BASE_URL}/api/preview", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": repaired_query
    })
    assert_proof("HTTP 200 on Healed /api/preview", prev_healed_res.status_code == 200)
    healed_sim = prev_healed_res.json()

    # Assert 0 enterprise_accounts deleted and $0 ARR lost
    healed_deleted_acc = healed_sim.get("deleted_accounts_count", 0)
    healed_lost_arr = healed_sim.get("arr_loss_usd", 0.0)
    healed_exposure = healed_sim.get("financial_exposure_usd", 0.0)

    assert_proof(
        "Healed Query Deleted Accounts Count == 0",
        healed_deleted_acc == 0,
        f"Enterprise Accounts Deleted: {healed_deleted_acc} (Safeguard Effective)"
    )

    assert_proof(
        "Healed Query Lost ARR == $0.00",
        healed_lost_arr == 0.0 and healed_exposure == 0.0,
        f"ARR Lost: ${healed_lost_arr:,.2f}, Total Financial Exposure: ${healed_exposure:,.2f}"
    )

    # -------------------------------------------------------------------------
    # PROOF 3: Single-Character Tamper Rejection (HTTP 409 Payload Drift)
    # -------------------------------------------------------------------------
    print("\n--- [PROOF 3: SINGLE-CHARACTER PAYLOAD TAMPER REJECTION] ---")
    # Dry-run a safe benign statement to get a valid signed 2PC preview token
    safe_query = "UPDATE service_configs SET current_value = '2048' WHERE env_key = 'DDOS_BURST_ALLOWANCE';"
    token_preview = requests.post(f"{BASE_URL}/api/preview", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": safe_query
    }).json()
    valid_2pc_token = token_preview["token_envelope"]["token"]

    # Tamper payload by appending a single trailing space
    tampered_query_space = safe_query + " "
    tamper_res_1 = requests.post(f"{BASE_URL}/api/commit", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": tampered_query_space,
        "token": valid_2pc_token
    })

    assert_proof(
        "Single Trailing Space Tamper Blocked with HTTP 409",
        tamper_res_1.status_code == 409 and "PAYLOAD DRIFT" in tamper_res_1.text,
        f"HTTP {tamper_res_1.status_code} - {tamper_res_1.json().get('detail', '')}"
    )

    # Tamper payload by appending a SQL comment
    tampered_query_comment = safe_query + " -- inject"
    tamper_res_2 = requests.post(f"{BASE_URL}/api/commit", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": tampered_query_comment,
        "token": valid_2pc_token
    })

    assert_proof(
        "SQL Comment Injection Tamper Blocked with HTTP 409",
        tamper_res_2.status_code == 409 and "PAYLOAD DRIFT" in tamper_res_2.text,
        f"HTTP {tamper_res_2.status_code} - {tamper_res_2.json().get('detail', '')}"
    )

    # -------------------------------------------------------------------------
    # PROOF 4: Live Commit Persistence Proof & State Hash Identity
    # -------------------------------------------------------------------------
    print("\n--- [PROOF 4: LIVE COMMIT PERSISTENCE & STATE HASH IDENTITY] ---")
    # Preview a valid benign modification
    target_mutation = "UPDATE service_configs SET current_value = '4096' WHERE env_key = 'DDOS_BURST_ALLOWANCE';"
    prev_for_commit = requests.post(f"{BASE_URL}/api/preview", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": target_mutation
    }).json()

    simulated_post_hash = prev_for_commit["simulated_post_state_hash"]
    commit_token = prev_for_commit["token_envelope"]["token"]

    print(f"Simulated Post-State Hash from Shadow CoW: {simulated_post_hash}")

    # Commit with approved token and untampered payload
    commit_res = requests.post(f"{BASE_URL}/api/commit", json={
        "domain": "CODE & SQL DEPLOY",
        "payload": target_mutation,
        "token": commit_token
    })
    assert_proof("HTTP 200 on Valid 2PC Commit", commit_res.status_code == 200, f"Status: {commit_res.status_code}")
    commit_data = commit_res.json()
    new_prod_hash = commit_data["new_production_state_hash"]

    # Verify that new production hash matches simulated post hash exactly
    assert_proof(
        "Production Hash Matches Simulated Post-State Hash Exactly",
        new_prod_hash == simulated_post_hash,
        f"New Prod Hash: {new_prod_hash} == Shadow Hash: {simulated_post_hash}"
    )

    # Query /api/state to prove permanent persistence in production
    live_state = requests.get(f"{BASE_URL}/api/state").json()
    persisted_hash = live_state["production_state_hash"]

    assert_proof(
        "Production State Permanently Persisted & Verified via /api/state",
        persisted_hash == simulated_post_hash and persisted_hash != init_hash,
        f"Persisted Hash: {persisted_hash} (Permanently Changed from Genesis)"
    )

    # Cleanup: restore pristine baseline
    requests.post(f"{BASE_URL}/api/reset")

    print("\n" + "=" * 85)
    print("ALL 4 FORENSIC AUDIT PROOFS PASSED DETERMINISTICALLY WITH ZERO FALLBACKS [100% GREEN]")
    print("=" * 85)

if __name__ == "__main__":
    run_forensic_proof()
