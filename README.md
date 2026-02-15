# LexBridge Pro

LexBridge Pro helps civil-law trained learners bridge to U.S. MBE-style concepts through short comparative lessons.

## Local development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Publish (GitHub Pages)

This repo includes `.github/workflows/deploy-pages.yml` to publish `dist/` to GitHub Pages.

1. Push this repo to GitHub.
2. In **Settings → Pages**, set **Source** to **GitHub Actions**.
3. Push to `main` (or run the workflow manually).
4. The site will be published at your GitHub Pages URL shown in the workflow output.

> If your repository name is not the root user/org site, add a `base` value in `vite.config.js`.
