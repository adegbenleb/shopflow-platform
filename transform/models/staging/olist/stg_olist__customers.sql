with source as (
    select * from {{ source('olist', 'olist_customers') }}
),

renamed as (
    select
        'olist'::text                           as tenant_id,
        customer_id                             as order_customer_id,
        customer_unique_id                      as customer_id,
        customer_zip_code_prefix                as postal_code,
        initcap(trim(customer_city))            as city,
        upper(trim(customer_state))             as state,
        _loaded_at,
        _source_file
    from source
)

select * from renamed