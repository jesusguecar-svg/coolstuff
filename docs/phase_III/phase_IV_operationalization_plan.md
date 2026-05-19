# Phase IV Operationalization Plan
## Texas General Lines Life, Accident & Health Prep Package

> Purpose: turn the current architecture + templates into a fully operable prep product.

## 1) Operating Definition of Done
Product is considered fully operative when all conditions are true:
1. All National units (N1–N8) and Texas chapters (TX1–TX4) are populated beyond placeholders.
2. Unit mini reviews, checkpoint forms (CP1–CP5), and mastery forms (M1–M3) are authored and internally reviewed.
3. QBank metadata tags are consistently applied and rationales include source backlinks.
4. Video/audio scripts exist for all clusters A–E and are mapped to unit checkpoints.
5. Remediation routing from checkpoints/mastery to QBank sets is executable.

## 2) Workstreams and Ownership

### WS-A Content Production
- Owner: Curriculum team
- Scope:
  - Fill N3, N4, N7, N8
  - Fill TX2, TX3, TX4
  - Finalize cram sheets and unit reviews for all units
- Exit criteria:
  - each file has objectives, key terms, section outline, assessment blueprint, linkage blocks complete

### WS-B Assessment Production
- Owner: Assessment design team
- Scope:
  - Complete CP2, CP4, CP5
  - Convert CP1 and CP3 blueprints into authoring-ready forms A/B
  - Fill M1–M3 with weighted item allocation plans
- Exit criteria:
  - every checkpoint/mastery file has item counts, difficulty split, and remediation thresholds fixed

### WS-C QBank Operationalization
- Owner: QBank/data team
- Scope:
  - apply taxonomy in `qbank/tag_taxonomy.md`
  - implement Sprint 1 tag maps plus remaining unit maps
  - enforce rationale schema with source path backlinks
- Exit criteria:
  - zero items missing required tags
  - zero items missing rationale backlink fields

### WS-D Media Production
- Owner: Media team
- Scope:
  - fill video/audio templates for clusters A–E
  - attach run-time budgets and unit linkage IDs
- Exit criteria:
  - each cluster has at least one overview clip and one trap-focused clip

### WS-E QA + Release Readiness
- Owner: QA/operations
- Scope:
  - coverage QA (domains 1–13)
  - weighting QA (item and instruction alignment)
  - remediation path QA (checkpoint/mastery to QBank)
- Exit criteria:
  - QA checklist pass with no P0/P1 defects

## 3) Recommended Sequencing
1. **Sprint 2 (highest priority completion):** N3, N4, TX2, CP2, related QBank maps
2. **Sprint 3 (health/law completion):** N7, N8, TX3, TX4, CP4, CP5
3. **Sprint 4 (simulation + polish):** M1–M3, full media pass, final cram sheet tuning
4. **Sprint 5 (go-live readiness):** end-to-end QA, pilot cohort, release notes

## 4) Operational Gates

### Gate G1 — Content Completeness
- Required pass:
  - all unit/chapter templates complete
  - no placeholder markers like `[TBD]` in core fields

### Gate G2 — Assessment Integrity
- Required pass:
  - checkpoints and mastery forms have fixed score rules
  - remediation logic documented per form

### Gate G3 — QBank Integrity
- Required pass:
  - tag completeness = 100%
  - rationale schema completeness = 100%

### Gate G4 — Media Linkage
- Required pass:
  - every unit cluster has mapped video/audio reinforcement

### Gate G5 — Pilot Readiness
- Required pass:
  - a sample student can traverse:
    read → mini review → checkpoint → remediation → mastery

## 5) QA Checklist (Executable)
- Domain coverage matrix complete for 1–13.
- Weighted emphasis matrix aligns with architecture tiers.
- CP1–CP5 threshold behavior documented and consistent.
- Mastery score-band behavior documented and consistent.
- All files cross-linked (unit ↔ checkpoint ↔ QBank ↔ media ↔ cram).

## 6) Risks and Mitigations
- **Risk:** content drift away from weighted domains.
  - **Mitigation:** enforce weight matrix review at each sprint close.
- **Risk:** QBank tags become inconsistent across authors.
  - **Mitigation:** lint-like metadata checks before merge.
- **Risk:** media over-compresses legal nuance.
  - **Mitigation:** keep legal exception-heavy topics reading-first with media as reinforcement only.

## 7) Immediate Next 5 Tasks (Actionable)
1. Fill `license_manual/N3_application_underwriting_delivery.md`.
2. Fill `license_manual/N4_retirement_other_life_concepts.md`.
3. Fill `texas_supplement/TX2_tx_life_only_rules.md`.
4. Upgrade `checkpoints/CP2_operations_retirement.md` to CP1/CP3 detail level.
5. Add `qbank/sprint_2_tag_maps.md` for N3/N4/TX2.

## 8) Tracking Metrics
- Template completion % by workstream
- Assessment blueprint completion %
- QBank tag completeness %
- Media linkage completeness %
- Gate pass/fail status (G1–G5)

This plan is the operational bridge from architecture to a releasable prep product.
