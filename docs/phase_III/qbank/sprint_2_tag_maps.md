# QBank Sprint 2 Tag Maps (N3, N4, TX2)

## Purpose
Define tag-map implementation for Sprint 2 priorities and align remediation with CP2 outcomes.

## N3 (Domains 3,9)
- Subtopics:
  - application_integrity
  - underwriting_evidence
  - delivery_requirements
  - replacement_workflow
  - field_underwriting_flags
- Primary trap types:
  - role_confusion
  - timing_trap
  - qualifier_ignore

## N4 (Domain 4)
- Subtopics:
  - retirement_vehicle_types
  - qualified_vs_nonqualified
  - accumulation_vs_distribution
  - rollover_logic
  - beneficiary_outcomes
- Primary trap types:
  - definition_swap
  - exception_misread

## TX2 (Domain 11)
- Subtopics:
  - texas_life_replacement
  - texas_life_disclosures
  - life_policy_standards
  - beneficiary_protection_rules
- Primary trap types:
  - timing_trap
  - role_confusion
  - exception_misread

## CP2 Remediation Link Rules
- If D3 <65%: assign `QB-N3-FLOW` + `QB-N3-ROLES`.
- If D4 <65%: assign `QB-N4-CORE` + `QB-N4-COMPARE`.
- If D9 <65%: assign field-underwriting scenario block + `QB-N3-TIMING`.

## Rationale Backlink Standard
All Sprint 2 items must include:
1. Correct-answer reason
2. Likely-distractor debunk
3. Source path (`Manual/Supplement > Unit > Section`)
4. Trap label
