with source as (
    select * from {{ source('olist', 'olist_order_reviews') }}
),

renamed as (
    select
        'olist'::text                                       as tenant_id,
        review_id,
        order_id,
        review_score::int                                   as score,
        nullif(trim(review_comment_title), '')              as comment_title,
        nullif(trim(review_comment_message), '')            as comment_message,
        nullif(review_creation_date, '')::timestamp         as created_at,
        nullif(review_answer_timestamp, '')::timestamp      as answered_at,
        _loaded_at,
        _source_file
    from source
),

-- Olist repeats some reviews. Keep one row per (review_id, order_id): the latest answer.
deduplicated as (
    select
        *,
        row_number() over (
            partition by review_id, order_id
            order by answered_at desc nulls last
        ) as row_num
    from renamed
)

select
    tenant_id, review_id, order_id, score,
    comment_title, comment_message, created_at, answered_at,
    _loaded_at, _source_file
from deduplicated
where row_num = 1
