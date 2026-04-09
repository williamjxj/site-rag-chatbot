# Repository Guidelines

## Project Structure & Module Organization
- `frontend/` hosts the Next.js interface (`app/` for routes, `components/` for UI, `lib/` for API helpers, `public/` for static assets, `tests/` for UI/e2e fixtures).
- `backend/` contains the FastAPI service (`src/app.py`, `src/config.py`, `src/services/` for RAG + LLM logic, `tests/` for API suites). Keep infra files (Docker, env samples) at repo root.
- Shared contracts (e.g., auth payloads) live in `frontend/types/` and `backend/src/schemas/`; keep them in sync when changing response shapes.

## Build, Test, and Development Commands
- Frontend dev server: `pnpm dev` (hot reload Next.js UI on http://localhost:3000).
- Frontend production build: `pnpm build && pnpm start` (runs Next.js static/SSR compilation, then boots the Node server).
- Frontend linting: `pnpm lint` (Next.js ESLint config).
- Frontend unit/UI tests: `pnpm test` or `pnpm test:watch` (Jest + Testing Library).
- Frontend e2e tests: `pnpm test:e2e` (Playwright, requires dev server running).
- Backend: `uvicorn backend.src.app:app --reload` for local dev, `pytest backend/tests` for API coverage.

## Coding Style & Naming Conventions
- TypeScript/React components use PascalCase; utility hooks/functions use camelCase; files mirror their default export name (e.g., `chat-interface.tsx`).
- Prefer functional React components, Tailwind for styling, and shadcn/ui primitives for consistent spacing/typography.
- Python backend follows Black formatting, Ruff lint rules, and snake_case for modules and functions. Keep configuration in `.env` files and reference via `pydantic` settings.

## Testing Guidelines
- Co-locate Jest specs under `tests/` (e.g., `tests/components/chat.interface.test.tsx`) and name files `*.test.ts(x)`.
- Mock network calls with MSW or fetch stubs; avoid hitting production APIs in tests.
- Backend tests belong in `backend/tests/` with descriptive names like `test_chat_routes.py`; include regression cases for every bug fix.
- Aim for meaningful coverage of parsing, auth, and LLM-selection branches before submitting PRs.

## Commit & Pull Request Guidelines
- Follow the existing Conventional Commits style seen in `git log` (`feat:`, `fix:`, `docs:`, etc.) so changelogs remain readable.
- Every PR should describe scope, testing evidence (`pnpm test`, `pytest`), and link to related issues. Attach screenshots or terminal output for UI-affecting changes.
- Highlight configuration impacts (new env vars, secrets) and update docs/`components.json` when adding UI libraries or design tokens.

## Security & Configuration Tips
- Never hardcode API keys; rely on `.env` files and `validate_api_keys()` in `backend/src/config.py`.
- Sanitize logs and client responses—surface generic errors to the UI while logging full tracebacks server-side.
- Rotate credentials when switching ACTIVE_LLM providers and ensure favicon/logo updates live under `frontend/public/` for Vercel deployments.
