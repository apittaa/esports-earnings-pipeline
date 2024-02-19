from pyspark.sql.types import *

ESPORTS_TOURNAMENTS_SCHEMA = StructType([
    StructField('EndDate', DateType(), nullable=True),
    StructField('GameId', IntegerType(), nullable=True),
    StructField('Location', StringType(), nullable=True),
    StructField('StartDate', DateType(), nullable=True),
    StructField('Teamplay', IntegerType(), nullable=True),
    StructField('TotalUSDPrize', FloatType(), nullable=True),
    StructField('TournamentId', IntegerType(), nullable=True),
    StructField('TournamentName', StringType(), nullable=True)
])

ESPORTS_GAMES_GENRE_SCHEMA = StructType([
    StructField('GameName', StringType(), nullable=True),
    StructField('Genre', StringType(), nullable=True),
    StructField('GameId', IntegerType(), nullable=True)
])

ESPORTS_GAMES_AWARDING_PRIZE_MONEY_SCHEMA = StructType([
    StructField('GameId', IntegerType(), nullable=True),
    StructField('GameName', StringType(), nullable=True),
    StructField('TotalPlayers', IntegerType(), nullable=True),
    StructField('TotalTournaments', IntegerType(), nullable=True),
    StructField('TotalUSDPrize', FloatType(), nullable=True)
])

ESPORTS_TOURNAMENTS_TYPES = {
    'EndDate': DateType(),
    'GameId': IntegerType(),
    'Location': StringType(),
    'StartDate': DateType(),
    'Teamplay': IntegerType(),
    'TotalUSDPrize': FloatType(),
    'TournamentId': IntegerType(),
    'TournamentName': StringType()
}

ESPORTS_GAMES_GENRE_TYPES = {
    'GameName': StringType(),
    'Genre': StringType(),
    'GameId': IntegerType()
}

ESPORTS_GAMES_AWARDING_PRIZE_MONEY_TYPES = {
    'GameId': IntegerType(),
    'GameName': StringType(),
    'TotalPlayers': IntegerType(),
    'TotalTournaments': IntegerType(),
    'TotalUSDPrize': FloatType()
}
