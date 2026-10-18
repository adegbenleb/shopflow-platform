-- Grain: one row per marketing lead. Did it become a seller, how fast, and what did that seller sell?
with leads as (
    select * from {{ ref('stg_olist__leads') }}
),

deals as (
    select * from {{ ref('stg_olist__closed_deals') }}
),

seller_sales as (
    select
        tenant_id,
        seller_id,
        count(distinct order_id)    as orders_sold,
        sum(price)                  as revenue
    from {{ ref('stg_olist__order_items') }}
    group by tenant_id, seller_id
)

select
    l.tenant_id,
    l.lead_id,
    l.lead_source,
    l.first_contact_date,
    d.lead_id is not null                                       as is_won,
    d.won_at,
    (d.won_at::date - l.first_contact_date)                     as days_to_close,
    d.business_segment,
    d.lead_type,
    case when d.seller_id is not null
         then md5(d.tenant_id || '|' || d.seller_id) end        as seller_key,
    coalesce(s.orders_sold, 0)                                  as seller_orders,
    coalesce(s.revenue, 0)                                      as seller_revenue
from leads l
left join deals d
    on l.tenant_id = d.tenant_id and l.lead_id = d.lead_id
left join seller_sales s
    on d.tenant_id = s.tenant_id and d.seller_id = s.seller_id
