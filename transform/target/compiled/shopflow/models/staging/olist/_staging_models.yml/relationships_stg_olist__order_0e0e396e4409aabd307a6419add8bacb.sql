
    
    

with child as (
    select order_customer_id as from_field
    from "shopflow"."analytics_staging"."stg_olist__orders"
    where order_customer_id is not null
),

parent as (
    select order_customer_id as to_field
    from "shopflow"."analytics_staging"."stg_olist__customers"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


