with src as (
    select
        admission_id,
        patient_id,
        doctor_id,
        hospital_id,
        insurance_id,
        condition_id,
        date_of_admission,
        discharge_date,
        room_number,
        admission_type,
        billing_amount
    from {{ source('healthcare', 'admission') }}
)

select * from src
