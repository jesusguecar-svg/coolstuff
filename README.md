# LexMap Pro

LexMap Pro is a progressive web app for comparative legal study between Venezuelan/Latin American Civil Law traditions and US Common Law.

## Stack

- React 18 (single-file app shell in `index.html`)
- Tailwind CSS (CDN)
- Lucide React icons
- Firebase v9 modular SDK (Auth + Firestore)

## Key features

- Auto-auth flow: `signInWithCustomToken` fallback to `signInAnonymously`
- Firestore profile path: `/artifacts/{appId}/users/{uid}/profile/data`
- Real-time profile sync with `onSnapshot`
- Onboarding + dashboard + full-screen lesson modal wizard
- Legal concept graph (`CONCEPT_DATA`) with EQUIVALENT/ANALOGOUS bridges
- PWA setup via `manifest.webmanifest` and `sw.js`
- Local fallback mode when Firebase config is not injected (progress stored in browser `localStorage`)

## Local run

```bash
python3 -m http.server 4173
```

Open: `http://localhost:4173`

## Environment injection

Set these globals before app boot in your hosting shell if available:

- `window.__firebase_config` (JSON object or JSON string)
- `window.__FIREBASE_CONFIG` (alternative config key)
- `window.__initial_auth_token` (optional custom auth token)
- `window.__app_id` (optional app namespace)
