with src as (
    select
        hospital_id,
        hospital_name
    from {{ source('healthcare', 'hospital') }}
)

select * from src
