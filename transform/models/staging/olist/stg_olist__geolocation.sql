-- The raw table has many rows per postal code (one per address sample).
-- We keep one row per postal code: average coordinates, and one city/state name.
with source as (
    select * from {{ source('olist', 'olist_geolocation') }}
)

select
    'olist'::text                                   as tenant_id,
    geolocation_zip_code_prefix                     as postal_code,
    round(avg(geolocation_lat::numeric), 6)         as latitude,
    round(avg(geolocation_lng::numeric), 6)         as longitude,
    min(initcap(trim(geolocation_city)))            as city,
    min(upper(trim(geolocation_state)))             as state,
    max(_loaded_at)                                 as _loaded_at
from source
group by geolocation_zip_code_prefix
