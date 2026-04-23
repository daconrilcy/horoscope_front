flowchart TD
    A[Mutation audit detected] --> B[Current audit review]
    A --> C[Audit review event history]

    B --> D{Review outcome}
    D -->|alert needed| E[Alert event]
    D -->|no alert| Z[Closed at audit level]

    E --> F[Delivery attempts]
    E --> G[Current alert handling]
    E --> H[Alert handling history]

    I[Suppression rules] --> J[Suppression application]
    J --> E

    G --> K{Handling decision}
    K -->|resolved| L[Alert closed]
    K -->|incident| M[Incident linked]
    K -->|follow-up| N[Follow-up scheduled]
    K -->|suppressed| J