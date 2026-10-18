with source as (
    select * from {{ source('olist', 'olist_products') }}
),

translation as (
    select * from {{ source('olist', 'product_category_name_translation') }}
),

renamed as (
    select
        'olist'::text                                       as tenant_id,
        s.product_id,
        coalesce(t.product_category_name_english,
                 s.product_category_name,
                 'unknown')                                 as category,
        nullif(s.product_weight_g, '')::numeric             as weight_g,
        nullif(s.product_length_cm, '')::numeric            as length_cm,
        nullif(s.product_height_cm, '')::numeric            as height_cm,
        nullif(s.product_width_cm, '')::numeric             as width_cm,
        nullif(s.product_photos_qty, '')::int               as photo_count,
        s._loaded_at,
        s._source_file
    from source s
    left join translation t
        on s.product_category_name = t.product_category_name
)

select * from renamed
