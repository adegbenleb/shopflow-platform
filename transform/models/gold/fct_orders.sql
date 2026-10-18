-- Grain: one row per order.
with orders as (
    select * from {{ ref('stg_olist__orders') }}
),

customers as (
    select * from {{ ref('stg_olist__customers') }}
),

items as (
    select
        tenant_id,
        order_id,
        count(*)                as item_count,
        sum(price)              as items_total,
        sum(freight_value)      as freight_total
    from {{ ref('stg_olist__order_items') }}
    group by tenant_id, order_id
),

payments as (
    select
        tenant_id,
        order_id,
        count(*)                as payment_count,
        sum(amount)             as payment_total,
        max(installments)       as max_installments
    from {{ ref('stg_olist__payments') }}
    group by tenant_id, order_id
),

reviews as (
    select
        tenant_id,
        order_id,
        avg(score)::numeric(3, 2)   as review_score
    from {{ ref('stg_olist__order_reviews') }}
    group by tenant_id, order_id
)

select
    o.tenant_id,
    o.order_id,
    md5(o.tenant_id || '|' || c.customer_id)                    as customer_key,
    o.status,
    o.purchased_at,
    o.purchased_at::date                                        as order_date,
    o.delivered_at,
    o.estimated_delivery_date,
    coalesce(i.item_count, 0)                                   as item_count,
    coalesce(i.items_total, 0)                                  as items_total,
    coalesce(i.freight_total, 0)                                as freight_total,
    coalesce(p.payment_total, 0)                                as payment_total,
    coalesce(p.payment_count, 0)                                as payment_count,
    p.max_installments,
    r.review_score,
    extract(day from o.delivered_at - o.purchased_at)::int      as delivery_days,
    o.delivered_at::date > o.estimated_delivery_date            as is_late
from orders o
left join customers c
    on o.tenant_id = c.tenant_id and o.order_customer_id = c.order_customer_id
left join items i
    on o.tenant_id = i.tenant_id and o.order_id = i.order_id
left join payments p
    on o.tenant_id = p.tenant_id and o.order_id = p.order_id
left join reviews r
    on o.tenant_id = r.tenant_id and o.order_id = r.order_id
