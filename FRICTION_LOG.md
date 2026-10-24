
# AWS / MCP Friction Log

**Project:** EduAgent Interview Coach  
**Purpose:** Document real development friction encountered while setting up AWS, Bedrock, MCP, or the simulated agent workflow.

> Record only issues you actually encounter. Never include API keys, credentials, access tokens, account IDs, or other private information. Verify the official event rules before assuming this log qualifies for a judging bonus.

## Severity Scale

- **S0 — Blocker:** Prevents the demo or submission.
- **S1 — High:** Core integration is unavailable.
- **S2 — Medium:** A workaround exists but creates a meaningful limitation.
- **S3 — Low:** Minor inconvenience.

## Issue Log

| Date/time (IST) | Component | Expected outcome | Actual result / reproduction | Workaround | Severity | Evidence | Status |
|---|---|---|---|---|---|---|---|
| 2026-10-21 18:09 | Environment / Python | `python -m venv .venv` creates virtual environment | Microsoft Store alias triggered error: `Python was not found` | Used `py -m venv .venv` using the official Windows Python Launcher | S3 | Exit code 1; `where.exe python` points to WindowsApps before real binary | Resolved |

## Detailed Issues

### Issue: Windows Python App Execution Alias Interception

- **Date/time (IST):** 2026-10-21 18:09
- **Component:** Environment / Python / PowerShell
- **Expected outcome:** `python -m venv .venv` creates virtual environment.
- **Actual result:** `python` command resolved to `C:\Users\ahmta\AppData\Local\Microsoft\WindowsApps\python.exe` which failed with error: `Python was not found; run without arguments to install from the Microsoft Store...`
- **Steps to reproduce:** Run `python -m venv .venv` in standard PowerShell when Windows App Execution Aliases are active.
- **Sanitized error message:** `Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Apps > Advanced app settings > App execution aliases.`
- **Workaround:** Used Windows Python Launcher `py -m venv .venv` which resolves to the installed Python 3.14.7 runtime at `C:\Users\ahmta\AppData\Local\Python\bin\python.exe`.
- **Severity:** S3
- **Evidence or reference:** Exit code 1; `where.exe py; where.exe python`.
- **Status:** Resolved
- **Lesson learned:** In Windows PowerShell environments with Microsoft Store aliases, invoke `py` or the explicit binary path `.venv\Scripts\python.exe` rather than bare `python`.

---

## Detailed Issue Template

### Issue: [Short descriptive title]

- **Date/time (IST):**
- **Component:** AWS / Bedrock / MCP / Simulator
- **Expected outcome:**
- **Actual result:**
- **Steps to reproduce:**
- **Sanitized error message:**
- **Workaround:**
- **Severity:** S0 / S1 / S2 / S3
- **Evidence or reference:**
- **Status:** Open / Investigating / Resolved
- **Lesson learned:**

---

## Notes

- Log the problem when it occurs, not from memory days later.
- Include the actual workaround and whether it solved the issue.
- Do not fabricate failures to make the log appear substantial.
- Never commit secrets or sensitive information.
- Do not claim a judging bonus unless the official rules confirm it.
