{{ config(materialized='table') }}

select
    *
from {{ ref('stg_esports_tournaments') }}
where Teamplay = 0
order by StartDate desc
