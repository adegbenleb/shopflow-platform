with source as (
    select * from {{ source('olist', 'olist_order_payments') }}
),

renamed as (
    select
        'olist'::text                               as tenant_id,
        order_id,
        payment_sequential::int                     as payment_number,
        lower(trim(payment_type))                   as payment_type,
        payment_installments::int                   as installments,
        payment_value::numeric(12, 2)               as amount,
        _loaded_at,
        _source_file
    from source
)

select * from renamed
