select
    hospital_id as hospital_key,
    hospital_name
from {{ ref('stg_hospital') }}
