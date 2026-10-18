with source as (
    select * from {{ source('olist', 'olist_order_items') }}
),

renamed as (
    select
        'olist'::text                                   as tenant_id,
        order_id,
        order_item_id::int                              as line_number,
        product_id,
        seller_id,
        nullif(shipping_limit_date, '')::timestamp      as ship_by_at,
        price::numeric(12, 2)                           as price,
        freight_value::numeric(12, 2)                   as freight_value,
        _loaded_at,
        _source_file
    from source
)

select * from renamed