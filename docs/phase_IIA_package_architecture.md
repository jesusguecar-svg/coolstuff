# Phase II-A: Premium Prep Package Architecture
## Texas General Lines Life, Accident & Health Agent Exam

> Scope: This document defines product/package architecture only (not final lesson prose, quiz items, calendars, or tracker logic).

---

## SECTION 1: PACKAGE DESIGN PHILOSOPHY

### 1) Why split into a National Manual and a Texas Supplement
- **Cognitive separation:** National product mechanics (policy types, riders, underwriting workflows) require concept modeling, while Texas law requires statute/rule recall and jurisdiction-specific distinctions.
- **Maintenance advantage:** Texas law updates can be revised in a standalone supplement without destabilizing national instructional flow.
- **Assessment fidelity:** Exam prep can mirror test cognition: “What is insurance logic?” vs “What does Texas require?”
- **Commercial UX parity:** This mirrors premium prep norms where students complete broad insurance content first, then state law precision pass.

### 2) How exam weights drive chapter depth and emphasis
Use blueprint weights as **instructional minutes + page depth + item volume** drivers:
- **Tier A (15–16%):** Deepest treatment (Life policy types; Life riders/provisions; Health policy types; Health provisions/riders).
- **Tier B (12–14%):** High-detail operational/legal units (Application/underwriting/delivery; Texas common statutes/rules).
- **Tier C (8%):** Medium depth (Retirement concepts; Field underwriting procedures).
- **Tier D (3–7%):** Focused concise modules with high-yield memorization frames (Social insurance; Other concepts; TX life-only; TX A&H-only; HMO).

### 3) How unit design balances concepts, memorization, and exam traps
Every unit should intentionally include three lanes:
1. **Concept lane:** Product purpose, risk transfer logic, claim/payment flow, suitability intent.
2. **Memory lane:** Time limits, notices, conversion rights, continuation provisions, required disclosures.
3. **Trap lane:** Similar-sounding terms, “always/never” distractors, role confusion (agent vs insurer), and timing misdirection.

### 4) Why Checkpoints, QBank, and Mastery Exams are staged differently
- **Checkpoint Exams:** Post-cluster competence gates; verify integrated understanding before progression.
- **QBank:** Continuous diagnostic drill by tag (domain/subtopic/trap type) for remediation.
- **Mastery Exams:** Late-stage full simulation under exam-like pressure and mixed-topic distribution.

### 5) How this reduces first-attempt failure risk
- Front-loads high-weight domains.
- Prevents “false confidence” from random drilling by requiring checkpoint gates.
- Forces legal precision in a dedicated law phase.
- Adds targeted remediation loops before final simulation.
- Creates layered retention (read → mini review → checkpoint → QBank → video/audio recap → mastery).

---

## SECTION 2: CORE PACKAGE COMPONENTS

## 1) License Exam Manual (National)
- **Purpose:** Core conceptual curriculum for General Knowledge domains (1–9).
- **When used:** Primary learning spine, first major phase.
- **Contains:** Structured units, explanations, examples, diagrams, key-term blocks, mini reviews.
- **Does not contain:** Texas statute text/citations as primary instruction.
- **Detail level:** Highest depth in Tier A/B weighted domains.

## 2) State Law Supplement (Texas)
- **Purpose:** Dedicated Texas statutes/rules coverage for domains 10–13.
- **When used:** After national base is built; then revisited before mastery.
- **Contains:** Black-letter law summaries, plain-English interpretation, comparison tables, law-focused drills.
- **Does not contain:** Broad product theory already mastered in national manual.
- **Detail level:** Dense and citation-aware; concise explanations with exact rule anchors.

## 3) Cram Sheets (National + Texas)
- **Purpose:** Rapid recall and pre-exam compression artifacts.
- **When used:** End of each unit cluster + final 72-hour review.
- **Contains:** Definitions, timelines, eligibility/trigger grids, exclusions/rider contrasts, “must-not-miss” traps.
- **Does not contain:** Long narrative teaching.
- **Detail level:** 1–3 pages per unit cluster.

## 4) Unit Quizzes / Embedded Mini Reviews
- **Purpose:** Immediate retrieval practice and misconception detection.
- **When used:** At end of each lesson chunk.
- **Contains:** Short mixed items (concept + memory + trap).
- **Does not contain:** Full-length simulation behavior.
- **Detail level:** 5–12 items per subunit.

## 5) Checkpoint Exams
- **Purpose:** Gate progression after related units.
- **When used:** After each major cluster.
- **Contains:** Mixed-item exams across a coherent unit set with performance-by-tag output.
- **Does not contain:** Full exam-length stress simulation.
- **Detail level:** Medium-length, sufficient to detect weak subdomains.

## 6) Topic-Based QBank
- **Purpose:** Adaptive drilling for mastery by granular tags.
- **When used:** Throughout; especially after weak checkpoint/mastery results.
- **Contains:** Taggable items, rationale links back to source units, difficulty scaling.
- **Does not contain:** Standalone replacement for reading sequence.
- **Detail level:** High volume, variable lengths (10/20/40 item drills).

## 7) Video Review
- **Purpose:** Visual reinforcement of structures, workflows, and comparisons.
- **When used:** After first read + after first checkpoint in a cluster.
- **Contains:** Short explainers, flow diagrams, side-by-side product/rider contrasts.
- **Does not contain:** Citation-dense statute parsing as sole format.
- **Detail level:** 4–9 minute micro-lessons.

## 8) Audio Review
- **Purpose:** Portable repetition for terms, distinctions, and timing rules.
- **When used:** Commute/review windows after primary learning.
- **Contains:** High-yield memory prompts, “if you see X, think Y” cues.
- **Does not contain:** Diagram-dependent concepts requiring visuals.
- **Detail level:** 3–7 minute clips; bundled by cluster.

## 9) Mastery Exam
- **Purpose:** Final readiness simulation and go/no-go signal.
- **When used:** End stage only, after checkpoints and remediation.
- **Contains:** Weighted blueprint representation, timed conditions, mixed difficulty, state+national blend.
- **Does not contain:** Immediate reteaching inside stem text.
- **Detail level:** Full-length high-fidelity simulation.

## 10) Optional Instructor Guidance Layer
- **Purpose:** Coaching for pacing, interpretation disputes, and remediation planning.
- **When used:** At checkpoint failures, plateau points, and pre-mastery triage.
- **Contains:** Office hours, study prescriptions, weak-area sprint plans.
- **Does not contain:** Replacement of independent reading/drilling.
- **Detail level:** Light-touch but high-leverage interventions.

---

## SECTION 3: LICENSE EXAM MANUAL ARCHITECTURE (NATIONAL)

### A. Recommended Unit Order and Domain Mapping

1. **Unit N1 — Life Policy Foundations: Term, Permanent, and Use Cases**
   - Domains: **1**
   - Rationale: Establishes core vocabulary and product categories.

2. **Unit N2 — Life Policy Riders, Provisions, Options, Exclusions**
   - Domains: **2**
   - Rationale: Builds on N1 with contractual detail and test traps.

3. **Unit N3 — Application, Underwriting, Policy Delivery (Life/A&H Context)**
   - Domains: **3 + 9 (bridge)**
   - Rationale: Operational lifecycle before product expansion.

4. **Unit N4 — Retirement & Other Life-Adjacent Concepts**
   - Domains: **4**
   - Rationale: Mid-weight concept set best learned after life fundamentals.

5. **Unit N5 — Health Policy Types and Core Plan Structures**
   - Domains: **5**
   - Rationale: Mirrors N1 for health side; high exam weight.

6. **Unit N6 — Health Provisions, Clauses, Riders, and Cost-Sharing Logic**
   - Domains: **6**
   - Rationale: Detailed contract interpretation and frequent distractor zone.

7. **Unit N7 — Social Insurance Programs**
   - Domains: **7**
   - Rationale: Distinct public-program framework; compact but tested.

8. **Unit N8 — Other Insurance Concepts & Integrated Field Underwriting Review**
   - Domains: **8 + 9 (consolidation)**
   - Rationale: Integrates remaining concepts with applied field underwriting judgment.

### B. Relative Depth by Weight
- **Longest units:** N1, N2, N5, N6.
- **Second-tier depth:** N3.
- **Medium units:** N4, N8.
- **Compact unit:** N7.

### C. Instructional Asset Placement
- **Graphics:** At beginning of N1/N5 (product maps) and N3/N8 (workflow maps).
- **Worked examples:** Mid-unit in N2/N6 for rider/provision interpretation.
- **Exercises:** End of each subunit; mixed question types.
- **Mini quizzes:** End of every unit.
- **Discussion prompts (optional coaching layer):** End of N3, N6, N8.
- **National cram sheets:** After N2 (Life Contracts), N6 (Health Contracts), N8 (Final National High-Yield).

---

## SECTION 4: TEXAS SUPPLEMENT ARCHITECTURE

### A. Chapter Order and Domain Coverage

1. **TX1 — Texas Common Statutes/Rules for Life & Health**
   - Covers Domain **10** (weight 14)
2. **TX2 — Texas Life-Only Statutes/Rules**
   - Covers Domain **11** (weight 6)
3. **TX3 — Texas A&H-Only Statutes/Rules**
   - Covers Domain **12** (weight 7)
4. **TX4 — Texas HMO Statutes/Rules**
   - Covers Domain **13** (weight 3)

### B. Black-Letter vs Plain-English Layering (inside each chapter)
- **Part A: Rule Text Layer** — precise legal requirement summaries with citation anchors.
- **Part B: Plain-English Layer** — exam-facing meaning, scope limits, and likely distractors.
- **Part C: Exam Trap Layer** — “confused with” callouts and timeline traps.

### C. Citation-Driven Tables Placement
- Place at the **end of each subchapter**:
  - Requirement
  - Applicability
  - Timeframe/threshold
  - Exceptions
  - Citation field

### D. Texas Cram Sheet Placement
- After TX1: “Common Texas Law Rapid Recall”.
- After TX3: “Life vs A&H Texas Distinctions”.
- After TX4: “HMO Ultra-High-Yield One-Pager”.

### E. Highest Emphasis Topics (weight + confusion risk)
1. **TX1 (Domain 10)** — highest legal emphasis.
2. **TX3 (Domain 12)** — A&H rule distinctions frequently confused with national policy provisions.
3. **TX2 (Domain 11)** — moderate emphasis, high precision.
4. **TX4 (Domain 13)** — concise but non-skippable due to unique terminology.

---

## SECTION 5: UNIT-BY-UNIT PACKAGE MAP

| Unit | Package | Domain(s) | Why placed here | Learning objective | Key terms (examples) | Concept:Mem ratio | Exercises | Checkpoint later | Video/Audio | QBank tags |
|---|---|---|---|---|---|---|---|---|---|---|
| N1 Life Policy Foundations | License Manual | 1 | Foundational product taxonomy | Distinguish major life policy forms and fit | term, whole life, universal life, variable life, premium mode, cash value | 70:30 | Yes | Yes | Both | Yes |
| N2 Life Riders/Provisions | License Manual | 2 | High-weight contract interpretation | Apply rider/provision rules and exclusions | waiver, accidental death, grace period, reinstatement, nonforfeiture, incontestability | 55:45 | Yes | Yes | Both | Yes |
| N3 Application/Underwriting/Delivery | License Manual | 3, 9 | Operational bridge across product lines | Sequence compliant application-to-delivery actions | insurable interest, replacement, disclosure, conditional receipt, suitability, producer report | 60:40 | Yes | Yes | Both | Yes |
| N4 Retirement & Other Life Concepts | License Manual | 4 | Moderate-weight conceptual extension | Compare retirement vehicles and tax-treatment basics at exam depth | annuity, qualified plan, rollover, beneficiary, accumulation/distribution | 65:35 | Yes | Yes | Video priority | Yes |
| N5 Health Policy Types | License Manual | 5 | Highest-weight health foundation | Identify plan types and intended use cases | major medical, disability income, long-term care, dental/vision, limited benefit | 70:30 | Yes | Yes | Both | Yes |
| N6 Health Provisions/Clauses/Riders | License Manual | 6 | Heavy test-trap zone | Interpret provisions, coordination, renewability, exclusions | deductible, copay, coinsurance, coordination of benefits, renewability, elimination period | 50:50 | Yes | Yes | Both | Yes |
| N7 Social Insurance | License Manual | 7 | Distinct public-program framework | Differentiate social insurance structures at licensing level | Social Security, Medicare, Medicaid, disability standards | 45:55 | Yes | Yes | Audio priority | Yes |
| N8 Other Concepts + Field UW Integration | License Manual | 8, 9 | Integrative capstone for remaining national topics | Apply field underwriting cues and miscellaneous concepts in scenarios | anti-selection, risk class, producer duties, red flags | 55:45 | Yes | Yes | Both | Yes |
| TX1 Common Texas Life/Health Law | Texas Supplement | 10 | Largest Texas domain | Apply shared TX regulatory requirements correctly | commissioner, unfair trade, licensing standards, notices, records | 40:60 | Yes | Yes | Audio priority | Yes |
| TX2 Texas Life-Only Law | Texas Supplement | 11 | Life-specific legal precision | Distinguish TX life-only obligations from common rules | replacement, policy standards, beneficiary protections | 45:55 | Yes | Yes | Both | Yes |
| TX3 Texas A&H-Only Law | Texas Supplement | 12 | High confusion with national health terms | Apply TX A&H-specific compliance requirements | mandated provisions, renewability classes, claim rules | 45:55 | Yes | Yes | Both | Yes |
| TX4 Texas HMO Law | Texas Supplement | 13 | Small but unique legal vocabulary | Recognize HMO-specific statutory obligations | network, emergency care standards, grievance/appeal terms | 40:60 | Yes | Yes | Short video + audio | Yes |

---

## SECTION 6: CHECKPOINT ARCHITECTURE

### 1) Recommended number of checkpoints: **5**

1. **CP-1 (Life Core):** N1 + N2
2. **CP-2 (Operations + Retirement):** N3 + N4
3. **CP-3 (Health Core):** N5 + N6
4. **CP-4 (National Integration):** N7 + N8 + cumulative national mix
5. **CP-5 (Texas Law):** TX1 + TX2 + TX3 + TX4

### 2) Why these clusters
- Aligns with cognitive bundles used in exam stems.
- Prevents cross-cluster contamination before basics are stable.
- Keeps Texas law checkpoint discrete for legal precision diagnostics.

### 3) What checkpoints measure
- Domain comprehension
- Rule application under scenario framing
- Trap resistance
- Retention across adjacent units

### 4) Progression score guidance
- **Continue threshold:** 75% overall and no domain below 65%.
- **Borderline:** 70–74% triggers targeted remediation before progression.
- **Hold/review:** <70% requires mandatory remediation loop.

### 5) Weak performance protocol
1. Assign targeted QBank sets by weak tag.
2. Revisit corresponding cram sheet + video/audio micro-review.
3. Re-take a parallel checkpoint form.

### 6) Distinction from QBank and Mastery
- **Checkpoint:** Gate after a finite taught cluster.
- **QBank:** Flexible drill and remediation engine.
- **Mastery:** End-to-end readiness simulation with weighted distribution.

---

## SECTION 7: QBANK ARCHITECTURE

### 1) Tag schema (required)
- `jurisdiction`: national / texas
- `domain`: 1–13
- `unit_id`: N1…N8, TX1…TX4
- `subtopic`: granular objective label
- `difficulty`: easy / medium / hard
- `trap_type`: definition_swap, timing_trap, role_confusion, exception_misread, qualifier_ignore
- `concept_type`: concept / memory / application / hybrid
- `cognitive_skill`: recall / compare / apply / diagnose

### 2) Custom quiz generation rules
- Modes:
  1. **Unit Drill** (single unit, mixed difficulty)
  2. **Weak-Area Repair** (lowest 2–3 tags)
  3. **Exam-Weighted Mix** (blueprint proportional)
  4. **Trap Immunity Set** (single trap_type focus)
- Defaults: 20 questions, mixed difficulty, rationales on.

### 3) Rationale structure requirement
Each QBank rationale should include:
1. Why correct answer is correct.
2. Why chosen distractor is wrong.
3. “Review link”: `Manual/Supplement > Unit > Section` pointer.
4. Trap annotation (e.g., timing trap).

### 4) Role in remediation (without replacing unit learning)
- QBank unlock for a unit only after first-pass reading/mini-quiz.
- Poor QBank results route student back to source sections before additional drilling.
- QBank is **practice and diagnosis**, not primary instruction.

### 5) Interaction with checkpoints and mastery
- Checkpoints push weak tags into auto-generated QBank playlists.
- Mastery post-analysis auto-creates a “Final Remediation Pack” by domain+trap type.

---

## SECTION 8: VIDEO & AUDIO ARCHITECTURE

### Cluster A: Life Products + Life Provisions (N1–N2)
- **Video best for:** Product family maps, rider comparisons, cash value mechanics.
- **Audio best for:** Definition contrasts, provision timelines, exclusion reminders.
- **Reading-heavy items:** nuanced exclusions and option interactions.
- **When used:** After first read, then again pre-CP1.

### Cluster B: Application/UW/Delivery + Retirement (N3–N4)
- **Video best for:** Process workflows (application → underwriting → delivery).
- **Audio best for:** Compliance checkpoints and role-based duties.
- **Reading-heavy items:** retirement/tax nuances requiring careful wording.
- **When used:** After unit completion + pre-CP2 recap.

### Cluster C: Health Types + Health Provisions (N5–N6)
- **Video best for:** Plan architecture and cost-sharing comparisons.
- **Audio best for:** clause distinctions and renewability memory anchors.
- **Reading-heavy items:** edge-case provision wording and exception logic.
- **When used:** After unit learning, before/after CP3 depending on weak tags.

### Cluster D: Social/Other/Field UW (N7–N8)
- **Video best for:** scenario-based field underwriting judgment examples.
- **Audio best for:** social program eligibility and quick distinctions.
- **Reading-heavy items:** integrated scenario interpretation.
- **When used:** As reinforcement pre-CP4 and pre-mastery.

### Cluster E: Texas Law (TX1–TX4)
- **Video best for:** framework overviews and law-family distinctions.
- **Audio best for:** memorization of requirement triggers/timeframes.
- **Reading-heavy items:** black-letter legal distinctions and exceptions.
- **When used:** after each TX chapter, then consolidated before CP5 and mastery.

---

## SECTION 9: MASTERY-EXAM ARCHITECTURE

### 1) Number of mastery exams: **3 forms**
- **M1 Diagnostic Simulation:** first full run after all checkpoints passed.
- **M2 Readiness Simulation:** after remediation cycle.
- **M3 Final Confidence Simulation (optional but recommended):** 3–5 days pre-exam.

### 2) When to take
- Only after CP1–CP5 completion and minimum checkpoint thresholds met.

### 3) What they simulate
- Full-length, timed, mixed-topic licensing environment.
- Weighted approximation of blueprint (national + Texas distributions).
- Distractor density and wording style matching exam pressure.

### 4) Score band policy
- **<72% = Weak:** not ready; remediate by lowest-weighted-performance tags.
- **72–79% = Borderline:** targeted remediation + retest.
- **≥80% = Likely Ready:** maintain with light mixed drills + cram review.

### 5) Remediation after poor mastery performance
1. Domain-level gap report.
2. Subtopic + trap-type assignment list.
3. Mandatory source reread segments.
4. Focused QBank blocks (20–40 items each).
5. Reattempt next mastery form after recovery threshold.

### 6) How mastery differs from checkpoints/QBank
- **Mastery:** culmination readiness proof under realistic conditions.
- **Checkpoint:** stage-gate proof by cluster.
- **QBank:** iterative skill repair and confidence stabilization.

---

## SECTION 10: PHASE III HANDOFF (IMPLEMENTATION BLUEPRINT)

Phase III should build the following production artifacts exactly:

## A) License Exam Manual
- Detailed chapter outlines for N1–N8.
- Lesson-level objectives, key-term blocks, examples, exercise placeholders.
- Weight-adjusted page budgets (Tier A/B/C/D).
- End-of-unit mini-review specs.

## B) State Law Supplement
- Chapter builds for TX1–TX4 with dual-layer format:
  - black-letter legal requirement
  - plain-English exam interpretation
- Citation table templates for each subchapter.
- Law-focused mini-review specs.

## C) Cram Sheets
- National set: Life Contracts, Health Contracts, National Final Rapid Review.
- Texas set: Common Law, Life vs A&H Distinctions, HMO One-Pager.
- One-page and two-page format templates.

## D) Unit Reviews
- Mini-review blueprint per unit (item counts by concept/memory/trap balance).
- Answer explanation template with source back-reference fields.

## E) Checkpoint Exams
- CP1–CP5 blueprint maps (unit coverage, item counts, difficulty split).
- Progression threshold policy and remediation triggers.
- Parallel form requirements (A/B forms per checkpoint).

## F) QBank Categories
- Final tag taxonomy implementation.
- Quiz mode presets (Unit Drill, Weak-Area Repair, Exam-Weighted Mix, Trap Immunity).
- Rationale formatting standard with source pointers.

## G) Video Scripts
- Script outlines for cluster-level micro-lessons (A–E clusters).
- Duration targets per clip and visual asset notes.
- “Do not over-compress” flags for reading-heavy topics.

## H) Audio Scripts
- High-yield audio recap scripts aligned to cram sheets.
- Prompt-response style memory cues.
- Clip bundling specs by cluster and total runtime targets.

## I) Mastery Exams
- 3-form mastery blueprint with weighted distributions.
- Timing, interface, and scoring specs.
- Post-exam remediation report schema.

---

## File Placement Recommendation for GitHub Upload
- Save this artifact as:
  - `docs/phase_IIA_package_architecture.md`
- If Phase 1 research memos are not yet in-repo, upload them to:
  - `docs/research/phase_1_memos/` (one memo per domain/chapter, `.md` format)

This keeps architecture (Phase II-A) separated from source research inputs and simplifies Phase III build sequencing.
