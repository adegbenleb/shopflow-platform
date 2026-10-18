-- Grain: one row per product line in an order. Used for buying-behaviour questions.
with items as (
    select * from {{ ref('stg_olist__order_items') }}
),

orders as (
    select tenant_id, order_id, order_customer_id, purchased_at
    from {{ ref('stg_olist__orders') }}
),

customers as (
    select tenant_id, order_customer_id, customer_id
    from {{ ref('stg_olist__customers') }}
)

select
    i.tenant_id,
    i.order_id,
    i.line_number,
    md5(i.tenant_id || '|' || c.customer_id)        as customer_key,
    md5(i.tenant_id || '|' || i.product_id)         as product_key,
    md5(i.tenant_id || '|' || i.seller_id)          as seller_key,
    o.purchased_at::date                            as order_date,
    i.price,
    i.freight_value
from items i
join orders o
    on i.tenant_id = o.tenant_id and i.order_id = o.order_id
left join customers c
    on o.tenant_id = c.tenant_id and o.order_customer_id = c.order_customer_id
