# Solomon Agency — Request a Case Quote Widget

## Part 1: UX / Scoring / Conversion / Carrd Safety Overview

- **Lead qualifier, not a calculator.** The widget estimates fit, turnaround, and a starting price range — it is not a binding price quote. Language is deliberately scoped ("estimated range," "scope-based pricing," "backend support") to avoid misrepresentation.
- **Scoring drives segmentation.** A single additive score (case complexity + urgency + support scope + file condition + volume) maps to four result bands that route leads toward the right next step — a direct quote request for straightforward cases, or an intro call for complex ones.
- **Rush override preserves trust.** When Rush urgency is selected, turnaround is overridden to "24–48 hours" *except* for extremely high-complexity cases (score 16+), where custom review is needed regardless. A "Rush pricing may apply" note keeps expectations honest.
- **Conversion-optimized CTAs.** Each band displays a contextually appropriate call-to-action. Low/mid complexity cases get a single "Request a Case Quote" button. Higher complexity shows dual CTAs (quote + intro call). The highest band funnels exclusively to an intro call to prevent sticker shock.
- **Non-legal-representation framing.** Every result includes the disclaimer: "All work is provided as backend operational support for attorney review and approval." The widget never implies direct client representation or guaranteed outcomes.
- **Carrd namespace isolation.** All CSS classes use `.sa-quote-widget` / `.saqw-*` prefixes. All element IDs start with `saqw-`. JavaScript runs in an IIFE with zero global variables. A scoped CSS reset inside `.sa-quote-widget` prevents Carrd styles from leaking in.
- **Accessible and mobile-first.** Proper `<label>`/`for` associations, `<fieldset>`/`<legend>` for checkbox groups, `aria-live` result region, `role="alert"` validation, keyboard-visible focus rings, 44px+ tap targets, and `prefers-reduced-motion` support.
- **Hidden summary field for handoff.** After scoring, a pipe-delimited summary string is written to a hidden `<input>` (`#saqw-estimate-summary`) that Carrd forms or third-party tools can capture for email/CRM routing.

---

## File Structure

```
solomon-quote-widget/
  css/sa-quote-widget.css      ← Part 2: HEAD CSS
  html/sa-quote-widget.html    ← Part 3: Inline HTML
  js/sa-quote-widget.js        ← Part 4: Body-end JavaScript
  preview.html                 ← Local test harness (open in browser)
  README.md                    ← This file (Parts 1 & 5)
```

---

## Part 5: Carrd Installation Instructions

### Prerequisites

- Carrd **Pro Standard** or **Pro Plus** plan (required for Embed elements)

### Step-by-step

1. **Add the CSS (Head embed)**
   - In your Carrd editor, click **+** → **Embed** → set **Type** to **Code**
   - Set **Style** to **Hidden** and **Position** to **Head**
   - Wrap the contents of `css/sa-quote-widget.css` in `<style>...</style>` tags and paste it in
   - Example:
     ```html
     <style>
       /* paste entire contents of css/sa-quote-widget.css here */
     </style>
     ```

2. **Add the HTML (Inline embed)**
   - Click **+** → **Embed** → set **Type** to **Code**
   - Set **Style** to **Inline**
   - Paste the entire contents of `html/sa-quote-widget.html` into the code field
   - Position this embed element where you want the widget to appear on your page

3. **Add the JavaScript (Body-end embed)**
   - Click **+** → **Embed** → set **Type** to **Code**
   - Set **Style** to **Hidden** and **Position** to **Body (End)**
   - Wrap the contents of `js/sa-quote-widget.js` in `<script>...</script>` tags and paste it in
   - Example:
     ```html
     <script>
       /* paste entire contents of js/sa-quote-widget.js here */
     </script>
     ```

4. **Wire up CTA anchor links**
   - The widget's CTA buttons link to `#quote-form` and `#intro-call` by default
   - In your Carrd page, give your quote form section an **ID** of `quote-form`
   - Give your intro call / scheduling section an **ID** of `intro-call`
   - If you use different IDs, update the `CONFIG` object at the top of the JavaScript:
     ```js
     var CONFIG = {
       rootSelector: '.sa-quote-widget',
       quoteFormHref: '#your-form-id',
       introCallHref: '#your-call-id'
     };
     ```

5. **Publish and test**
   - Click **Publish** in Carrd
   - Test all form fields, verify results appear correctly
   - Test on mobile to confirm responsive layout
   - Check browser console for any JavaScript errors

### Local Preview

Open `preview.html` directly in any browser to test the widget without Carrd. No server or build tools required.
