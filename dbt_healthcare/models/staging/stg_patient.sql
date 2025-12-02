with src as (
    select
        patient_id,
        name,
        age,
        gender,
        blood_type
    from {{ source('healthcare', 'patient') }}
)

select * from src
