# Career document schema

This contract is a JSON Resume-aligned career record with plugin extensions. Standard JSON Resume sections (`basics`, `work`, `education`, `awards`, and `skills`) retain their familiar meaning. The extension fields below preserve provenance for evidence that commonly gets lost during resume editing.

## Required shape

```json
{
  "basics": {
    "name": "Full Name",
    "email": "name@example.com",
    "location": {
      "city": "City",
      "region": "Region"
    }
  },
  "work": [
    {
      "name": "Employer",
      "position": "Verified title",
      "startDate": "2020-01",
      "endDate": "2024-01",
      "highlights": [
        {
          "text": "Verified accomplishment",
          "source": "resume-2024.docx#work[0].highlights[2]"
        }
      ],
      "metrics": [
        {
          "statement": "Reduced cycle time",
          "value": "20%",
          "source": "review-2023.md#metric-4",
          "verificationNote": "Confirmed by user on 2026-09-18"
        }
      ]
    }
  ],
  "education": [],
  "awards": [
    {
      "title": "Award title",
      "date": "2023-05",
      "citation": "Verbatim award citation",
      "source": "award-citation.txt#paragraph-1"
    }
  ],
  "skills": [],
  "performanceReviews": [
    {
      "excerpt": "Verbatim review excerpt",
      "date": "2023-12",
      "reviewerRole": "Manager",
      "source": "review-2023.md#paragraph-7"
    }
  ],
  "metrics": [
    {
      "statement": "Improved retention",
      "value": "12%",
      "source": "metrics.xlsx#Sheet1!B4",
      "verificationNote": "User confirmed source and period"
    }
  ]
}
```

## Provenance rules

- Every plugin extension item must include a `source` pointer to the supplied input or an explicit user answer.
- Preserve quotes as quotes; do not turn an interpretation into a fact.
- Use `verificationNote` for how a metric or claim was confirmed, not for invented confidence.
- A missing, conflicting, or ambiguous field remains unresolved until the user answers a clarifying question.

The schema is intentionally documented as a contract rather than a closed JSON Schema so the upstream JSON Resume standard can evolve. Consumers must accept the standard sections and the named extension arrays above.
