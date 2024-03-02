{{config(materialized='view')}}

--handling deduplication
with esports_games_awarding_prize_money as
(
    select *,
        row_number() over(partition by GameId, GameName) as rn
    from {{ source('staging', "esports_games_awarding_prize_money") }}
)
select 
    -- identifiers
    cast(({{dbt_utils.surrogate_key(['GameId', 'GameName'])}}) as string) as case_id,
    cast(GameId as integer) as GameId,

    -- Tournament info
    cast(TotalTournaments as integer) as TotalTournaments,
    cast(TotalPlayers as integer) as TotalPlayers,
    cast(TotalUSDPrize as FLOAT64) as TotalUSDPrize,

    -- Game info
    cast(GameName as string) as GameName,
    cast(Genre as string) as Genre,
from esports_games_awarding_prize_money
where rn = 1

{% if var('is_test_run', default=false) %}

    limit 100

{% endif %}
