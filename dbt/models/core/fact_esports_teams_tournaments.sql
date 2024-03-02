{{ config(materialized='table') }}

select
    *
from {{ ref('stg_esports_tournaments') }}
where Teamplay = 1
order by StartDate desc