with src as (
    select
        medication_id,
        medication_name
    from {{ source('healthcare', 'medication') }}
)

select * from src
