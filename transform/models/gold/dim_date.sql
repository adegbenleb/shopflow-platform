-- A calendar table: one row per day. Facts join to it on order_date.
with days as (
    select generate_series('2016-01-01'::date, '2019-12-31'::date, interval '1 day')::date as date_day
)

select
    date_day,
    extract(year from date_day)::int            as year,
    extract(quarter from date_day)::int         as quarter,
    extract(month from date_day)::int           as month,
    to_char(date_day, 'Month')                  as month_name,
    extract(isodow from date_day)::int          as day_of_week,
    extract(isodow from date_day) in (6, 7)     as is_weekend
from days
