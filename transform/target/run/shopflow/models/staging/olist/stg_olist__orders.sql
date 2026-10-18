
  create view "shopflow"."analytics_staging"."stg_olist__orders__dbt_tmp"
    
    
  as (
    with source as (
    select * from "shopflow"."raw_olist"."olist_orders"
),

renamed as (
    select
        'olist'::text                                           as tenant_id,
        order_id,
        customer_id                                             as order_customer_id,
        order_status                                            as status,
        nullif(order_purchase_timestamp, '')::timestamp         as purchased_at,
        nullif(order_approved_at, '')::timestamp                as approved_at,
        nullif(order_delivered_carrier_date, '')::timestamp     as shipped_at,
        nullif(order_delivered_customer_date, '')::timestamp    as delivered_at,
        nullif(order_estimated_delivery_date, '')::date         as estimated_delivery_date,
        _loaded_at,
        _source_file
    from source
)

select * from renamed
  );