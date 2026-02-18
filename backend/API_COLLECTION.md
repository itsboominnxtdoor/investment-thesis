# Thesis Engine API - Postman/Insomnia Collection

Import this collection into Postman or Insomnia for API testing.

## Base URL
```
http://localhost:8000/api/v1
```

## Environment Variables

Set these variables in your API client:
- `base_url`: `http://localhost:8000/api/v1`
- `company_id`: UUID of a test company
- `ticker`: `AAPL` (or any ticker)

---

## Companies

### List Companies
```
GET {{base_url}}/companies
```

### List Companies with Filters
```
GET {{base_url}}/companies?search=Apple&sector=Technology&exchange=NASDAQ
```

### Get Company by ID
```
GET {{base_url}}/companies/{{company_id}}
```

### Get Company by Ticker
```
GET {{base_url}}/companies/ticker/{{ticker}}
```

---

## Financials

### List Financial Snapshots
```
GET {{base_url}}/companies/{{company_id}}/financials
```

### Get Latest Financial Snapshot
```
GET {{base_url}}/companies/{{company_id}}/financials/latest
```

### Ingest Financials (from FMP)
```
POST {{base_url}}/companies/{{company_id}}/financials/ingest
```

---

## Business Profile

### Get Business Profile
```
GET {{base_url}}/companies/{{company_id}}/business-profile
```

### Generate Business Profile (LLM)
```
POST {{base_url}}/companies/{{company_id}}/business-profile/generate
```

---

## Thesis

### List Thesis Versions
```
GET {{base_url}}/companies/{{company_id}}/thesis?page=1&per_page=10
```

### Get Latest Thesis
```
GET {{base_url}}/companies/{{company_id}}/thesis/latest
```

### Generate Thesis (LLM)
```
POST {{base_url}}/companies/{{company_id}}/thesis/generate
```

---

## Quarterly Updates

### List Quarterly Updates
```
GET {{base_url}}/companies/{{company_id}}/quarterly-updates
```

### Generate Quarterly Update (LLM)
```
POST {{base_url}}/companies/{{company_id}}/quarterly-updates/generate
```

---

## Documents

### List Documents
```
GET {{base_url}}/companies/{{company_id}}/documents
```

### Ingest Documents (from EDGAR/SEDAR)
```
POST {{base_url}}/companies/{{company_id}}/documents/ingest
```

---

## Health Check

### API Health
```
GET {{base_url}}/health
```

---

## Example Workflow

1. **Seed companies** (CLI):
   ```bash
   python scripts/seed_companies.py
   ```

2. **Get company by ticker**:
   ```
   GET /api/v1/companies/ticker/AAPL
   ```
   Copy the `id` from response.

3. **Ingest financials**:
   ```
   POST /api/v1/companies/{id}/financials/ingest
   ```

4. **Generate business profile**:
   ```
   POST /api/v1/companies/{id}/business-profile/generate
   ```

5. **Generate thesis**:
   ```
   POST /api/v1/companies/{id}/thesis/generate
   ```

6. **View results**:
   ```
   GET /api/v1/companies/{id}/thesis/latest
   ```
