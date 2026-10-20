with source as (
    select * from {{ source('olist', 'olist_closed_deals') }}
),

renamed as (
    select
        'olist'::text                                           as tenant_id,
        mql_id                                                  as lead_id,
        seller_id,
        sdr_id,
        sr_id,
        nullif(won_date, '')::timestamp                         as won_at,
        nullif(trim(business_segment), '')                      as business_segment,
        nullif(trim(lead_type), '')                             as lead_type,
        nullif(trim(lead_behaviour_profile), '')                as lead_behaviour_profile,
        nullif(has_company, '')::boolean                        as has_company,
        nullif(has_gtin, '')::boolean                           as has_gtin,
        nullif(trim(business_type), '')                         as business_type,
        nullif(declared_product_catalog_size, '')::numeric      as declared_catalog_size,
        nullif(declared_monthly_revenue, '')::numeric(14, 2)    as declared_monthly_revenue,
        _loaded_at,
        _source_file
    from source
)

select * from renamed
