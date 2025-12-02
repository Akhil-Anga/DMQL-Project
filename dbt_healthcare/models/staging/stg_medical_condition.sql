with src as (
    select
        condition_id,
        condition_name
    from {{ source('healthcare', 'medical_condition') }}
)

select * from src
