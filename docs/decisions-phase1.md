## Phase 1 decisions

### Layers: staging, then gold (silver later)
Staging holds one model per raw table per tenant: types fixed, canonical names, tenant_id added.
Gold holds the star schema. Silver (combining tenants) is skipped until a second tenant exists,
because with one tenant it would be an empty extra step.

### Duplicate reviews
Olist repeats some reviews. Staging keeps one row per (review_id, order_id), the latest answer.
Duplicates would distort review counts and average scores.

### Geolocation
The raw table has many rows per postal code. Staging keeps one row per postal code,
with averaged coordinates.

### Customer identity
Olist creates a new customer_id per order. We rename it order_customer_id and use
customer_unique_id as customer_id, the real person.

### Keys and privacy in gold
Gold uses surrogate keys: md5(tenant_id || '|' || natural_id). They are stable,
tenant-safe, and do not expose raw IDs. Postal codes are cut to a 3-digit area.

### One pipeline
canonical_pipeline runs load_raw, then dbt build (all models and tests in dependency order).

### Database credentials
All containers read POSTGRES_USER, POSTGRES_PASSWORD and POSTGRES_DB from the same
variables in compose.yml (set in docker/.env). The docker dbt target and the load_raw
DAG have no fallback, so a missing variable fails loudly instead of using a wrong default.
The dev dbt target keeps its fallback, because on the Mac convenience matters more.
