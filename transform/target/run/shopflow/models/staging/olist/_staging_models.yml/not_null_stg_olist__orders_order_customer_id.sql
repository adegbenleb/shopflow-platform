
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_customer_id
from "shopflow"."analytics_staging"."stg_olist__orders"
where order_customer_id is null



  
  
      
    ) dbt_internal_test