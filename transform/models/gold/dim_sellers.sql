select
    md5(tenant_id || '|' || seller_id)      as seller_key,
    tenant_id,
    seller_id,
    left(postal_code, 3) || '**'            as postal_area,
    city,
    state
from {{ ref('stg_olist__sellers') }}
