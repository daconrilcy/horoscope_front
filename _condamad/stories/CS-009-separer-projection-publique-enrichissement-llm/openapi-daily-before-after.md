# OpenAPI Daily Prediction Before / After

Endpoint verifie: `GET /v1/predictions/daily`

Source before: worktree temporaire detache sur `HEAD` (`4bcd0863`), operation extraite via `app.main.app.openapi()`.

Source after: arbre courant, operation extraite via `app.main.app.openapi()`.

Resultat: `same: true`

## Operation before

```json
{
  "operationId": "get_daily_prediction_v1_predictions_daily_get",
  "parameters": [
    {
      "in": "query",
      "name": "date",
      "required": false,
      "schema": {
        "anyOf": [
          {
            "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
            "type": "string"
          },
          {
            "type": "null"
          }
        ],
        "title": "Date"
      }
    },
    {
      "in": "header",
      "name": "authorization",
      "required": false,
      "schema": {
        "anyOf": [
          {
            "type": "string"
          },
          {
            "type": "null"
          }
        ],
        "title": "Authorization"
      }
    }
  ],
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/DailyPredictionResponse"
          }
        }
      },
      "description": "Successful Response"
    },
    "422": {
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/HTTPValidationError"
          }
        }
      },
      "description": "Validation Error"
    }
  },
  "summary": "Get Daily Prediction",
  "tags": [
    "predictions"
  ]
}
```

## Operation after

```json
{
  "operationId": "get_daily_prediction_v1_predictions_daily_get",
  "parameters": [
    {
      "in": "query",
      "name": "date",
      "required": false,
      "schema": {
        "anyOf": [
          {
            "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
            "type": "string"
          },
          {
            "type": "null"
          }
        ],
        "title": "Date"
      }
    },
    {
      "in": "header",
      "name": "authorization",
      "required": false,
      "schema": {
        "anyOf": [
          {
            "type": "string"
          },
          {
            "type": "null"
          }
        ],
        "title": "Authorization"
      }
    }
  ],
  "responses": {
    "200": {
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/DailyPredictionResponse"
          }
        }
      },
      "description": "Successful Response"
    },
    "422": {
      "content": {
        "application/json": {
          "schema": {
            "$ref": "#/components/schemas/HTTPValidationError"
          }
        }
      },
      "description": "Validation Error"
    }
  },
  "summary": "Get Daily Prediction",
  "tags": [
    "predictions"
  ]
}
```

## Commandes

```powershell
git worktree add --detach .tmp-cs009-openapi-before HEAD
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = ".tmp-cs009-openapi-before\backend"
Set-Location .tmp-cs009-openapi-before\backend
python -B - # extraction app.openapi()["paths"]["/v1/predictions/daily"]["get"]
Set-Location backend
python -B - # meme extraction sur l'arbre courant
git worktree remove .tmp-cs009-openapi-before --force
```
