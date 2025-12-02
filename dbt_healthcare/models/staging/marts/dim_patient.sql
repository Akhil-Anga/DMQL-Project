select
    patient_id as patient_key,
    name,
    age,
    gender,
    blood_type
from {{ ref('stg_patient') }}
