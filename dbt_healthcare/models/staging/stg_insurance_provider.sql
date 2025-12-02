with src as (
    select
        insurance_id,
        provider_name
    from {{ source('healthcare', 'insurance_provider') }}
)

select * from src
