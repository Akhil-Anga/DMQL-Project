select
    insurance_id as insurer_key,
    provider_name
from {{ ref('stg_insurance_provider') }}
