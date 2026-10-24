"""
AETHELGARD — Autonomous End-to-End Verification & Connectivity Test Suite (verify_e2e.py)
Validates all REST API endpoints, 2PC cryptographic flow, CoW shadow cloning,
deterministic state hashing, and data catalog integrity.
"""

import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"

def log_test(name: str, passed: bool, detail: str = ""):
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name:<45} {detail}")
    if not passed:
        sys.exit(1)

def run_e2e_tests():
    print("=" * 80)
    print("AETHELGARD E2E CONNECTIVITY & FUNCTIONALITY VERIFICATION SUITE")
    print(f"Target: {BASE_URL}")
    print("=" * 80)

    # 1. Test Static Frontend Root
    try:
        r = requests.get(f"{BASE_URL}/", timeout=5)
        log_test("GET / (Frontend Root Index)", r.status_code == 200, f"HTTP {r.status_code}, Length: {len(r.text)} bytes")
        assert "AETHELGARD" in r.text
        assert "three.min.js" in r.text
    except Exception as e:
        log_test("GET / (Frontend Root Index)", False, str(e))

    # 2. Test /api/state
    try:
        r = requests.get(f"{BASE_URL}/api/state", timeout=5)
        data = r.json()
        log_test("GET /api/state (System State & Catalog)", r.status_code == 200, f"Hash: {data['production_state_hash'][:16]}...")
        assert data["status"] == "OPERATIONAL"
        assert data["shadow_fork_status"] == "READY"
        summary = data["catalog_summary"]
        assert summary["enterprise_accounts_count"] == 16, f"Expected 16 accounts, got {summary['enterprise_accounts_count']}"
        assert summary["payment_ledger_count"] == 24, f"Expected 24 ledger rows, got {summary['payment_ledger_count']}"
        assert summary["service_configs_count"] == 10, f"Expected 10 configs, got {summary['service_configs_count']}"
        assert summary["outbound_mail_queue_count"] == 12, f"Expected 12 emails, got {summary['outbound_mail_queue_count']}"
    except Exception as e:
        log_test("GET /api/state (System State & Catalog)", False, str(e))

    # 3. Test /api/ledger
    try:
        r = requests.get(f"{BASE_URL}/api/ledger", timeout=5)
        data = r.json()
        log_test("GET /api/ledger (Audit Log)", r.status_code == 200, f"Entries: {len(data['ledger'])}")
        assert len(data["ledger"]) >= 1
    except Exception as e:
        log_test("GET /api/ledger (Audit Log)", False, str(e))

    # 4. Test /api/preview for SQL
    try:
        payload = "DELETE FROM enterprise_accounts WHERE status = 'SUSPENDED';"
        r = requests.post(f"{BASE_URL}/api/preview", json={"domain": "CODE & SQL DEPLOY", "payload": payload}, timeout=5)
        data = r.json()
        log_test("POST /api/preview (SQL Cascading Hazard)", r.status_code == 200, f"Blast Score: {data['blast_score']}, Mutated: {data['records_mutated']}")
        assert data["success"] is True
        assert data["blast_score"] > 20.0
        assert data["records_mutated"] > 0
        assert "token_envelope" in data
        assert data["token_envelope"]["signature"] is not None
        assert data["token_envelope"]["token"] is not None
        token_envelope = data["token_envelope"]
    except Exception as e:
        log_test("POST /api/preview (SQL Cascading Hazard)", False, str(e))

    # 5. Test /api/preview for Payment Ledger
    try:
        pay_payload = json.dumps({"action": "BATCH_REFUND", "account_id": "ACC-CORP-01", "iterations": 50, "amount_usd": 75000.0})
        r = requests.post(f"{BASE_URL}/api/preview", json={"domain": "PAYMENT LEDGER", "payload": pay_payload}, timeout=5)
        data = r.json()
        log_test("POST /api/preview (Payment Drain Loop)", r.status_code == 200, f"Blast: {data['blast_score']}, Exposure: ${data['financial_exposure_usd']:,.2f}")
        assert data["financial_exposure_usd"] > 100000.0
        assert "payment_ledger" in data["affected_nodes"]
    except Exception as e:
        log_test("POST /api/preview (Payment Drain Loop)", False, str(e))

    # 6. Test /api/preview for Outbound Email
    try:
        eml_payload = json.dumps({"recipient": "auditor@untrusted.com", "subject": "Keys", "body": "Access key AKIAIOSFODNN7EXAMPLE for S3."})
        r = requests.post(f"{BASE_URL}/api/preview", json={"domain": "OUTBOUND EMAIL", "payload": eml_payload}, timeout=5)
        data = r.json()
        log_test("POST /api/preview (Email Credential Leak)", r.status_code == 200, f"PII Score: {data['pii_leakage']['score']}, Findings: {len(data['pii_leakage']['findings'])}")
        assert data["pii_leakage"]["score"] >= 45.0
        assert any("AWS Access Key" in f for f in data["pii_leakage"]["findings"])
    except Exception as e:
        log_test("POST /api/preview (Email Credential Leak)", False, str(e))

    # 7. Test /api/heal (Self-Healing AST Synthesizer)
    try:
        dangerous_sql = "DROP TABLE payment_ledger;"
        r = requests.post(f"{BASE_URL}/api/heal", json={"domain": "CODE & SQL DEPLOY", "payload": dangerous_sql}, timeout=5)
        data = r.json()
        log_test("POST /api/heal (SQL DROP TABLE Repair)", r.status_code == 200, f"Changes: {len(data['patch']['changes_made'])}")
        assert "ARCHIVE" in data["patch"]["repaired_payload"]
        assert data["patch"]["status"] == "REPAIRED_DETERMINISTICALLY"
    except Exception as e:
        log_test("POST /api/heal (SQL DROP TABLE Repair)", False, str(e))

    # 8. Test 2PC Safe Commit Protocol
    try:
        # Dry-run a safe benign update to acquire preview token
        safe_query = "UPDATE service_configs SET current_value = '1500' WHERE env_key = 'DDOS_BURST_ALLOWANCE';"
        prev_res = requests.post(f"{BASE_URL}/api/preview", json={"domain": "CODE & SQL DEPLOY", "payload": safe_query}, timeout=5).json()
        valid_token = prev_res["token_envelope"]["token"]

        # Commit using the token
        commit_res = requests.post(
            f"{BASE_URL}/api/commit",
            json={"domain": "CODE & SQL DEPLOY", "payload": safe_query, "token": valid_token},
            timeout=5
        )
        data = commit_res.json()
        log_test("POST /api/commit (Valid 2PC Atomic Commit)", commit_res.status_code == 200, f"New Hash: {data['new_production_state_hash'][:16]}...")
        assert data["status"] == "COMMITTED_TO_PRODUCTION"
    except Exception as e:
        log_test("POST /api/commit (Valid 2PC Atomic Commit)", False, str(e))

    # 9. Test /api/benchmarks and run
    try:
        r = requests.get(f"{BASE_URL}/api/benchmarks", timeout=5)
        bench = r.json()
        log_test("GET /api/benchmarks (24 Cases List)", r.status_code == 200, f"Total Cases: {bench['total_cases']}")
        assert bench["total_cases"] == 24

        r2 = requests.post(f"{BASE_URL}/api/benchmarks/run", json={"test_id": "BENCH-SQL-01"}, timeout=5)
        data2 = r2.json()
        log_test("POST /api/benchmarks/run (Single Case)", r2.status_code == 200, f"Executed: {data2['executed_count']}, Latency: {data2['total_latency_ms']}ms")
        assert data2["executed_count"] == 1
    except Exception as e:
        log_test("GET /api/benchmarks and run", False, str(e))

    # 10. Test /api/redteam/run
    try:
        r = requests.post(f"{BASE_URL}/api/redteam/run", timeout=10)
        data = r.json()
        log_test("POST /api/redteam/run (All 5 Attack Vectors)", r.status_code == 200, f"Passed: {data['passed_count']}/{data['attack_vectors_count']}")
        assert data["all_passed"] is True
        assert data["passed_count"] == 5
    except Exception as e:
        log_test("POST /api/redteam/run (All 5 Attack Vectors)", False, str(e))

    # 11. Test /api/reset (Deterministic Baseline Restore)
    try:
        r = requests.post(f"{BASE_URL}/api/reset", timeout=5)
        data = r.json()
        log_test("POST /api/reset (Pristine Restore)", r.status_code == 200, f"Status: {data['status']}")
        assert data["status"] == "RESET_COMPLETED"
        assert data["catalog_summary"]["enterprise_accounts_count"] == 16
        assert data["catalog_summary"]["payment_ledger_count"] == 24
    except Exception as e:
        log_test("POST /api/reset (Pristine Restore)", False, str(e))

    print("=" * 80)
    print("ALL 11 END-TO-END VERIFICATION CHECKS PASSED DETERMINISTICALLY [100% GREEN]")
    print("=" * 80)

if __name__ == "__main__":
    run_e2e_tests()
