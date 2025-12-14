with base as (
    select
        a.admission_id                          as admission_key,
        a.patient_id                            as patient_key,
        a.doctor_id                             as doctor_key,
        a.hospital_id                           as hospital_key,
        a.insurance_id                          as insurer_key,
        a.condition_id                          as condition_key,
        a.date_of_admission,
        a.discharge_date,
        a.room_number,
        a.admission_type,
        a.billing_amount,
        test_result                               as tr
    from {{ ref('stg_admission') }} a
    left join {{ ref('stg_test_result') }} tr
        on a.admission_id = tr.admission_id
)

select * from base
