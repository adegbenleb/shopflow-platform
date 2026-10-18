
    
    

select
    order_customer_id as unique_field,
    count(*) as n_records

from "shopflow"."analytics_staging"."stg_olist__customers"
where order_customer_id is not null
group by order_customer_id
having count(*) > 1


