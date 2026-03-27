# Data Contracts

## Schemas

Schemas are defined in `schemas/` using JSON Schema (draft 2020-12).

### question_item.schema.json

Each question has these required fields:

| Field | Type | Description |
|---|---|---|
| `question_id` | string | `B{batch}-Q{seq}` (e.g., `B01-Q001`) |
| `rule_ids` | string[] | Regulatory/content rule references |
| `domain` | string | Top-level content domain |
| `subdomain` | string | Specific topic |
| `difficulty` | enum | `easy`, `medium`, `hard` |
| `format` | string | Question format (e.g., `direct_rule`, `application_scenario`) |
| `stem` | string | The question text |
| `options` | array | 4 objects: `{label: "A"|"B"|"C"|"D", text: string}` |
| `correct_answer` | enum | `A`, `B`, `C`, `D` |
| `correct_explanation` | string | Why the correct answer is right |
| `wrong_explanations` | object | Keys = wrong option labels, values = why each is wrong |
| `trap_type` | string\|null | Trap pattern code or null |
| `source_confidence` | enum | `high`, `medium`, `low` |
| `review_status` | enum | `draft`, `validated`, `flagged`, `rejected` |
| `status_history` | array | Audit trail of status changes |

### question_batch.schema.json

Wraps an array of question items with batch-level metadata:

| Field | Type | Description |
|---|---|---|
| `batch_id` | string | Batch identifier |
| `version` | string | Semver version |
| `generated_date` | string | ISO date |
| `generated_by` | string | Generator identity |
| `question_count` | integer | Number of questions in batch |
| `difficulty_distribution` | object | Counts by difficulty |
| `questions` | array | Array of question_item objects |

## Manifest

`data/questions_validated/validated_batches_manifest.json` is the single source of truth for which batches are active.

| Field | Description |
|---|---|
| `batches[].batch_id` | Batch identifier (e.g., `"01"`) |
| `batches[].file` | Filename of the batch JSON |
| `batches[].report` | Filename of the validation report |
| `batches[].question_count` | Expected question count |
| `batches[].status` | `approved` = active in pipeline |
| `normalization_log` | Record of filename normalizations and exclusions |

## Explanation Model

Every question uses:
- `correct_explanation`: explanation for the correct answer
- `wrong_explanations`: object keyed by wrong-answer labels (3 keys), each explaining why that option is incorrect

The `rationale_by_choice` field is **not used** and must not appear in validated files.
