with source as (
    select * from {{ source('olist', 'olist_marketing_qualified_leads') }}
),

renamed as (
    select
        'olist'::text                                       as tenant_id,
        mql_id                                              as lead_id,
        nullif(first_contact_date, '')::date                as first_contact_date,
        landing_page_id,
        coalesce(nullif(lower(trim(origin)), ''), 'unknown') as lead_source,
        _loaded_at,
        _source_file
    from source
)

select * from renamed
