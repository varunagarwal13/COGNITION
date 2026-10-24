# AETHELGARD: GSD SPEC-LOCK SPECIFICATION

## 1. PROBLEM STATEMENT & TRACK OBJECTIVE
- **Track & Problem:** Track 2, Problem 3 — Simulated Consequences Before Real Action
- **Core Purpose:** Autonomous AI agent dry-run simulation sandbox and cryptographic Two-Phase Commit (2PC) workbench that intercepts high-stakes autonomous agent actions across:
  1. Code & Database Deployments (SQL DDL/DML, foreign-key cascades, schema mutations)
  2. Payment & Treasury Processing (idempotency, refund loops, escrow releases, negative balance invariants)
  3. Outbound Email & Communication (PII/credential scanning, mass broadcast panic prevention)
- **Architectural Pipeline:** Strict mechanical separation between dry-run preview (`/api/preview`), auto-fix patch synthesis (`/api/heal`), and production commit (`/api/commit`).
- **Empirical Evaluation:** Quantitative benchmark evaluation across 24 realistic test cases (18 destructive hazards + 6 completely safe operations) achieving 100% recall (18/18 caught) and 0% false positives (6/6 safe allowed).

---

## 2. STRICT DESIGN TOKENS & MONOCHROMATIC BLUSH-PORCELAIN PALETTE
- `--bg-canvas-primary`: `#FCF8F8` (Main page background, 3D WebGL canvas clear color, and clean breathing room covering >55% of the viewport)
- `--bg-surface-secondary`: `#FBEFEF` (Left control sidebar, top navigation bar, and slide-over modal drawers)
- `--bg-card-tertiary`: `#F9DFDF` (Clickable scenario cards, natural-language input box fill, benchmark tracks, and hover highlights)
- `--brand-accent-coral`: `#F5AFAF` (Primary button fills, active stage pills, 3D primary node spheres, and expanding shockwave rings)
- `--ink-editorial-dark`: `#2B1919` (Deep rose-espresso ink derived from 0° hue of `#F5AFAF` — used strictly for crisp, high-contrast text, `1px solid #2B1919` structural borders, and `3px 3px 0px #2B1919` tactile button offset shadows)
- `--ink-editorial-muted`: `#6E4747` (Secondary captions, connecting rails, and helper hints)

### Zero-Tolerance Anti-Slop Rules
- **Typography:** `'Times New Roman', Times, serif` exclusively across 100% of headings, buttons, input fields, badges, and floating labels.
- **Forbidden Fonts:** No Inter, Roboto, Arial, or generic sans-serif fonts.
- **Forbidden Colors:** Zero old brown hex codes (`#FFDBBB`, `#CCBEB1`, `#997E67`, `#664930`) and zero default neon red/green/blue hex codes.
- **Zero Blurry Shadows:** No `box-shadow: 0 10px 25px rgba(...)`. Only crisp `1px solid #2B1919` hairline borders and hard tactile `3px 3px 0px #2B1919` offsets.

---

## 3. ZERO-FALLBACK EXECUTION GUARANTEES
- **Deterministic Shadow Isolation:** `/api/preview` must clone the live SQLite database in-memory (`prod_conn.backup(shadow_conn)`), execute actions within `<15ms`, and calculate exact row/financial diffs without touching production disk or state.
- **Counterfactual Ralph Self-Healing:** `/api/heal` must programmatically patch flawed SQL, payments, or emails, and verify within a dry-run clone that `blast_radius_score == 0.0` before returning the patch.
- **Cryptographic 2PC Attestation:** `/api/commit` requires an HMAC-SHA256 signature generated during preview, binding pre-state SHA-256 hash, payload SHA-256 hash, and TTL. Any single-character payload mutation or state drift rejects with `HTTP 409 Conflict`.
- **Center 3D Stage:** Must render using a hardware-accelerated `THREE.WebGLRenderer` with `renderer.setClearColor(0xFCF8F8, 1)`, interactive raycast node picking, and real-time mechanical consequence dial rotation.
