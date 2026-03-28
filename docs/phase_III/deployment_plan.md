# Deployment Plan — Phase Dashboard

## Goal
Deploy `docs/phase_III/dashboard/` as a usable team dashboard with a stable URL.

## Option A (Recommended): GitHub Pages from `/docs`
1. Push branch to GitHub.
2. In repository settings, open **Pages**.
3. Set source to **Deploy from a branch**.
4. Choose branch (`main`) and folder (`/docs`).
5. Save and wait for the first Pages deployment.
6. Access dashboard at:
   - `https://<org-or-user>.github.io/<repo>/phase_III/dashboard/`

### Why Option A
- Zero backend required.
- Works with current static HTML/CSS/JS.
- Easy to maintain in-repo with PR approvals.

## Option B: Vercel / Netlify static hosting
- Point hosting root to `docs/phase_III/dashboard`.
- Enable auto-deploy on merge to main.
- Keep URL in README and team docs.

## Post-Deployment Operations
- Assign one owner per workstream (WS-A..WS-E).
- Update dashboard weekly.
- Export JSON snapshot weekly and store in `docs/phase_III/status_snapshots/`.
- Review gate progression (G1..G5) in weekly ops call.

## Rollback Plan
- If dashboard UI breaks, revert to previous commit for `docs/phase_III/dashboard/*` and redeploy.
- No data loss risk for source docs; dashboard state is local browser storage + optional JSON export.

## Security/Privacy Notes
- Dashboard stores status in browser localStorage only.
- Do not store PII or credentials in task notes.
