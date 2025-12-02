select
    doctor_id as doctor_key,
    doctor_name
from {{ ref('stg_doctor') }}
