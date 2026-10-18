with source as (
    select * from {{ source('olist', 'olist_sellers') }}
),

renamed as (
    select
        'olist'::text                         as tenant_id,
        seller_id,
        seller_zip_code_prefix                as postal_code,
        initcap(trim(seller_city))            as city,
        upper(trim(seller_state))             as state,
        _loaded_at,
        _source_file
    from source
)

select * from renamed