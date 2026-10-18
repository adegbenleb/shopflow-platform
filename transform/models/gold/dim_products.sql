select
    md5(tenant_id || '|' || product_id)     as product_key,
    tenant_id,
    product_id,
    category,
    weight_g,
    length_cm,
    height_cm,
    width_cm,
    photo_count
from {{ ref('stg_olist__products') }}
