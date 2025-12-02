with src as (
    select
        doctor_id,
        doctor_name
    from {{ source('healthcare', 'doctor') }}
)

select * from src
