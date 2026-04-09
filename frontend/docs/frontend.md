# Frontend Overview

## Architecture & Framework
- Built with Next.js 14 (app router) + React 18 for server/edge flexibility, and Tailwind v4 (design tokens defined in `app/globals.css`) for styling.
- shadcn/ui primitives (`components/ui/`) provide consistent buttons, cards, tabs, while Lucide Icons, Framer Motion, and GSAP power the Amber Minimal visual language.
- Client data flows through lightweight API helpers under `lib/api/` (auth, chat, admin, ingest) that inject `Authorization` headers from `localStorage`; shared DTOs live in `types/`.
- Routes: `app/page.tsx` hosts the business chat hero + console, `app/admin/page.tsx` is the control room, `app/profile/page.tsx` renders subscriber details. Auth routes under `app/auth` handle sign‑in/out.

## Highlighted Features
- **Business-ready chat console**: motion-enhanced glass UI with contextual hero, concierge imagery, and animated messaging (Framer Motion + GSAP).
- **Real-time citation view**: Markdown renderer with Amber-themed code blocks and structured source chips.
- **Admin control room**: tabbed surface for uploads, document management, embedding provider switching, and ingestion triggers.
- **Subscriber workspace**: profile page aligning with business-tier messaging (status, SLA cues).
- **Automated screenshots**: `pnpm snapshots` runs Playwright to mock APIs and export PNGs in `public/screenshots/` for docs.

## Recommended TODOs
1. **Theme toggle / responsive polish**: add dark/light/business variations and ensure hero/chat layout scales perfectly on sub-13" laptops.
2. **Chat history + saved threads**: persist `messages` via backend/websocket channel so business users can revisit conversations.
3. **Admin analytics widgets**: surface ingestion KPIs, LLM usage, and warning banners inside `/admin`.
4. **Internationalization**: wrap copy in i18n hooks to support multilingual business audiences.
5. **Testing coverage**: add Jest/RTL specs for chat components and extend Playwright to cover admin interactions (upload mock, provider switch).
6. **Accessibility audit**: run axe/lighthouse to ensure contrast and focus states meet WCAG across the Amber palette.
