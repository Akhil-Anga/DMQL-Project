{{ config(materialized='view') }}

with src as (

    select
        test_result_id,
        admission_id,
        test_result
    from {{ source('healthcare', 'test_result') }}

)

select
    test_result_id,
    admission_id,
    test_result
from src
