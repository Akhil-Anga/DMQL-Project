select
    condition_id as condition_key,
    condition_name
from {{ ref('stg_medical_condition') }}
