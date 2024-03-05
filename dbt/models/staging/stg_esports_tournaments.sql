{{config(materialized='view')}}

--handling deduplication
with esports_tournaments as
(
    select *,
        row_number() over(partition by GameId, StartDate) as rn
    from {{ source('staging', "esports_tournaments") }}
)
select 
    -- identifiers
    cast(({{dbt_utils.generate_surrogate_key(['GameId', 'StartDate'])}}) as string) as case_id,
    cast(GameId as integer) as GameId,
    cast(TournamentId as integer) as TournamentId,

    -- Tournament info
    cast(TournamentName as string) as TournamentName,
    cast(Location as string) as Location,
    cast(Teamplay as integer) as Teamplay,
    cast(TotalUSDPrize as FLOAT64) as TotalUSDPrize,

    -- Game info
    cast(GameName as string) as GameName,
    cast(Genre as string) as Genre,

    -- Date
    cast(StartDate as date) as StartDate,
    cast(EndDate as date) as EndDate,
from esports_tournaments
where rn = 1

-- {% if var('is_test_run', default=true) %}

--     limit 100

-- {% endif %}
