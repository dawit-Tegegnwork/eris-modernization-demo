# Data model

```mermaid
erDiagram
  users ||--o{ regulatory_applications : submits
  users ||--o{ regulatory_applications : reviews
  users ||--o{ status_history : performs
  users ||--o{ application_comments : writes
  users ||--o{ audit_logs : triggers
  regulatory_applications ||--o{ document_checklist_items : has
  regulatory_applications ||--o{ status_history : tracks
  regulatory_applications ||--o{ application_comments : contains

  users {
    uuid id PK
    string email UK
    string full_name
    enum role
    string organization
    string password_hash
  }

  regulatory_applications {
    uuid id PK
    string reference_number UK
    enum application_type
    string product_name
    string applicant_org
    string description
    enum status
    uuid applicant_id FK
    uuid assigned_reviewer_id FK
    datetime submitted_at
    datetime created_at
    datetime updated_at
  }

  document_checklist_items {
    uuid id PK
    uuid application_id FK
    string doc_type
    string label
    bool required
    bool received
    string notes
  }

  status_history {
    uuid id PK
    uuid application_id FK
    string from_status
    string to_status
    uuid actor_id FK
    string note
    datetime created_at
  }

  application_comments {
    uuid id PK
    uuid application_id FK
    uuid author_id FK
    string body
    datetime created_at
  }

  audit_logs {
    uuid id PK
    string action
    uuid actor_id FK
    string entity_type
    string entity_id
    bool synthetic_only
    json metadata_json
    datetime created_at
  }
```

## Application types

- `product_registration` — new pharmaceutical product dossier
- `import_permit` — import authorization for regulated products
- `gmp_certificate` — GMP facility certification
- `variation_amendment` — post-approval change request

## Status values

- `draft` — created but not submitted
- `submitted` — awaiting reviewer pickup
- `under_technical_review` — assigned reviewer evaluating
- `clarification_requested` — reviewer needs more information
- `approved` — regulatory decision: approved
- `rejected` — regulatory decision: rejected
