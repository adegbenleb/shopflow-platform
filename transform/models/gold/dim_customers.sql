-- One row per real customer (person), per tenant.
-- PII rule: no raw IDs or full postal codes leave this layer.
with customers as (
    select * from {{ ref('stg_olist__customers') }}
),

latest as (
    select distinct on (tenant_id, customer_id)
        tenant_id,
        customer_id,
        postal_code,
        city,
        state
    from customers
    order by tenant_id, customer_id, _loaded_at desc
)

select
    md5(tenant_id || '|' || customer_id)            as customer_key,
    tenant_id,
    left(postal_code, 3) || '**'                    as postal_area,
    city,
    state
from latest
