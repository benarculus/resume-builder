# Job requirements artifact schema

The `job-requirements-planner` emits one JSON document per role. The `resume-drafter` consumes this exact shape; it must not infer alternate headings or parse free-form prose.

## Contract

```json
{
  "source": {
    "url": "https://example.com/jobs/123",
    "title": "Role title",
    "capturedAt": "2026-09-18"
  },
  "requiredQualifications": [
    {
      "id": "RQ-001",
      "text": "Required qualification copied or closely paraphrased from the posting",
      "source": "https://example.com/jobs/123#qualifications"
    }
  ],
  "preferredQualifications": [],
  "responsibilities": [
    {
      "id": "RESP-001",
      "text": "Responsibility stated by the posting",
      "source": "https://example.com/jobs/123#responsibilities"
    }
  ],
  "constraints": {
    "compensation": null,
    "level": "Senior",
    "location": "Remote - United States",
    "source": "https://example.com/jobs/123#details"
  }
}
```

## Validation rules

- `source.url` is the primary user-supplied posting link.
- `requiredQualifications`, `preferredQualifications`, and `responsibilities` are arrays. Each item has a stable `id`, factual `text`, and a `source` URL or pasted-text pointer.
- `constraints` always exists. Unknown values are `null`; do not guess compensation, level, or location.
- Supplementary links may be cited in individual `source` fields, but the planner must process only links explicitly supplied by the user.
- A requirement is not implied merely because it is common for a role or industry.
