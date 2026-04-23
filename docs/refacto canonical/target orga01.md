erDiagram
    CANONICAL_ENTITLEMENT_MUTATION_AUDITS ||--o| CANONICAL_ENTITLEMENT_MUTATION_AUDIT_REVIEWS : "has current review"
    CANONICAL_ENTITLEMENT_MUTATION_AUDITS ||--o| CANONICAL_ENTITLEMENT_MUTATION_AUDIT_REVIEW_EVENTS : "has review history"
    CANONICAL_ENTITLEMENT_MUTATION_AUDITS ||--o| CANONICAL_ENTITLEMENT_MUTATION_ALERT_EVENTS : "can produce alerts"

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_EVENTS ||--o| CANONICAL_ENTITLEMENT_MUTATION_ALERT_DELIVERY_ATTEMPTS : "has delivery attempts"
    CANONICAL_ENTITLEMENT_MUTATION_ALERT_EVENTS ||--o| CANONICAL_ENTITLEMENT_MUTATION_ALERT_HANDLINGS : "has current handling"
    CANONICAL_ENTITLEMENT_MUTATION_ALERT_EVENTS ||--o| CANONICAL_ENTITLEMENT_MUTATION_ALERT_HANDLING_EVENTS : "has handling history"
    CANONICAL_ENTITLEMENT_MUTATION_ALERT_EVENTS ||--o| CANONICAL_ENTITLEMENT_MUTATION_ALERT_SUPPRESSION_APPLICATIONS : "can be suppressed by rule"

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_SUPPRESSION_RULES ||--o| CANONICAL_ENTITLEMENT_MUTATION_ALERT_SUPPRESSION_APPLICATIONS : "applied to alerts"

    CANONICAL_ENTITLEMENT_MUTATION_AUDITS {
        int id PK
        string mutation_kind
        string mutation_scope
        string feature_code
        int plan_id
        string plan_code
        string actor_type
        string actor_identifier
        string risk_level
        datetime detected_at
        string request_id
        datetime created_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_AUDIT_REVIEWS {
        int id PK
        int audit_id FK
        string review_status
        int reviewed_by_user_id
        datetime reviewed_at
        text review_comment
        string incident_key
        int review_version
        string request_id
        datetime created_at
        datetime updated_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_AUDIT_REVIEW_EVENTS {
        int id PK
        int audit_id FK
        string event_type
        string previous_review_status
        string new_review_status
        text previous_review_comment
        text new_review_comment
        string previous_incident_key
        string new_incident_key
        int reviewed_by_user_id
        string request_id
        datetime occurred_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_EVENTS {
        int id PK
        int audit_id FK
        string dedupe_key UK
        string alert_kind
        string alert_status
        string risk_level_snapshot
        string review_status_snapshot
        string feature_code_snapshot
        int plan_id_snapshot
        string plan_code_snapshot
        string actor_type_snapshot
        string actor_identifier_snapshot
        int sla_target_seconds_snapshot
        datetime due_at_snapshot
        int age_seconds_snapshot
        string primary_delivery_channel
        string last_delivery_status
        text last_delivery_error
        int delivery_attempt_count
        datetime first_delivered_at
        datetime last_delivered_at
        boolean is_suppressed
        datetime suppressed_at
        string suppression_reason
        string request_id
        json payload
        datetime created_at
        datetime updated_at
        datetime closed_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_DELIVERY_ATTEMPTS {
        int id PK
        int alert_event_id FK
        int attempt_number
        string delivery_channel
        string delivery_provider
        string delivery_status
        text delivery_error
        int response_code
        boolean is_retryable
        string request_id
        json payload
        datetime created_at
        datetime delivered_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_HANDLINGS {
        int id PK
        int alert_event_id FK
        string handling_status
        string resolution_code
        int handled_by_user_id
        datetime handled_at
        text ops_comment
        string incident_key
        boolean requires_followup
        datetime followup_due_at
        string suppression_application_key
        int handling_version
        string request_id
        datetime created_at
        datetime updated_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_HANDLING_EVENTS {
        int id PK
        int alert_event_id FK
        string event_type
        string handling_status
        string resolution_code
        int handled_by_user_id
        datetime handled_at
        text ops_comment
        string incident_key
        boolean requires_followup
        datetime followup_due_at
        string suppression_application_key
        string request_id
        datetime occurred_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_SUPPRESSION_RULES {
        int id PK
        string alert_kind
        string feature_code
        string plan_code
        string actor_type
        string suppression_key
        string rule_status
        text ops_comment
        boolean is_active
        int created_by_user_id
        datetime created_at
        int updated_by_user_id
        datetime updated_at
    }

    CANONICAL_ENTITLEMENT_MUTATION_ALERT_SUPPRESSION_APPLICATIONS {
        int id PK
        int alert_event_id FK
        int suppression_rule_id FK
        string suppression_key
        string application_mode
        text application_reason
        int applied_by_user_id
        string request_id
        datetime applied_at
    }