---
name: sih26-e2e-verify
description: Verify and repair the SIH26 frontend-to-backend integration end to end.
agent: agent
---

Act as the integration-test and repair agent for the SIH26 AI Student Success frontend.

Production backend:
https://dropout-predictor-2pme.onrender.com

API base:
https://dropout-predictor-2pme.onrender.com/api/v1

Swagger:
https://dropout-predictor-2pme.onrender.com/docs

## Mission

Verify every frontend-to-backend integration described in `docs/SIH26_Frontend_Backend_E2E_Verification_Playbook.pdf` and in the live FastAPI OpenAPI contract. For each endpoint, confirm both the HTTP/API behavior and the user-visible React behavior. If a test fails, diagnose the root cause, fix the smallest correct part of the code, rerun the failed test and a related regression test, and continue until PASS or a genuine external blocker is identified.

## Non-negotiable rules

- The running FastAPI OpenAPI contract is the source of truth. Do not invent endpoint paths or payload fields.
- Use `VITE_API_URL` and the shared Axios client. Do not scatter hardcoded backend URLs.
- Do not replace real API integration with mocks to make tests pass.
- Do not duplicate XGBoost risk logic, SHAP, BKT, Gemini evaluation, next-question logic, prerequisite routing, or backend RBAC in React.
- Never send `expected_answer` or `is_correct` from the student Tutor UI.
- Treat valid empty arrays/zero counts as an empty-state UX case, not automatically as a backend failure.
- Never expose or commit passwords, JWTs, database URLs, Gemini keys, or WhatsApp tokens.
- For intervention approve/reject and Parent Report routes, discover the exact live endpoint before testing. If a route does not exist, mark it `NOT_IMPLEMENTED` instead of inventing it.

## Workflow

1. Inspect `package.json`, routes, auth context/store, `src/api`, environment usage, and existing tests.
2. Retrieve/inspect the live OpenAPI schema and build an actual endpoint inventory.
3. Compare frontend API functions with live paths, methods, request schemas, response shapes, and RBAC.
4. Reuse the existing test framework. If no browser E2E framework exists, add Playwright with minimal configuration.
5. Create direct API smoke tests and browser E2E tests for Auth, Student Dashboard, Mastery, Tutor, Learning Sessions, Faculty Analytics, EWS, Interventions, Admin, and Parent Reports if implemented.
6. Use credentials only from `E2E_*` environment variables.
7. Run tests against the deployed backend and local frontend.
8. For every failure, capture status code, response body, console/network error, expected behavior, actual behavior, and suspected root cause.
9. Fix only the root cause. Retest until PASS.
10. Create `docs/e2e-verification-report.md` with columns: Test ID | Endpoint | Role | API result | UI result | Status | Fix applied | Files changed | Notes.
11. At the end, run frontend build/lint/tests and summarize remaining `BLOCKED_EXTERNAL` or `NOT_IMPLEMENTED` items.

## Acceptance criteria

- Authentication and role redirects work.
- Protected requests carry Bearer JWT.
- 401/403/404/422/503 states behave correctly.
- Student `/me` pages render real backend data and safe empty states.
- Tutor session persists answers, feedback, mastery, next-question behavior and history.
- Faculty analytics/EWS charts and tables use real API data.
- Students cannot access another student's data.
- Faculty cannot impersonate student Tutor answers.
- Admin-only user management is protected.
- No relevant browser console errors remain.
- Production build succeeds.
- Verification report is complete.

Do not stop after only analyzing. Execute the tests, make safe code fixes when needed, rerun, and update the report after each repair cycle. Ask me before any destructive database operation or production data deletion.
