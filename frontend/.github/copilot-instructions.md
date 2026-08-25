# SIH26 repository instructions for GitHub Copilot

- Production API base: `https://dropout-predictor-2pme.onrender.com/api/v1`.
- FastAPI/OpenAPI is the source of truth for paths, payloads, roles, and response shapes.
- Frontend is React + Vite + Tailwind + Axios + React Router + Recharts + Lucide.
- Keep all API calls behind shared modules in `src/api`; use one Axios client configured by `VITE_API_URL`.
- Attach JWT Bearer tokens in the shared Axios interceptor. On 401 clear auth and redirect to login; on 403 show unauthorized state.
- Never move XGBoost, SHAP, LangGraph, BKT, Gemini evaluation, Tutor next-question selection, prerequisite routing, or backend RBAC logic into React.
- Students use `/student-dashboard/me` for their own dashboard. Never allow a student to change `student_code` to inspect another student.
- Tutor UI never sends `expected_answer` or `is_correct`.
- Charts must use real API data. Valid empty arrays/zero counts require polished empty states, not fake data.
- Do not hardcode passwords, JWTs, database URLs, Gemini keys, WhatsApp tokens, or other secrets.
- For undocumented action routes such as intervention approve/reject, inspect the live OpenAPI contract before implementing or testing.
- Prefer small root-cause fixes. After each integration change, rerun the affected test plus one nearby regression flow.
