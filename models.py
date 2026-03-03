from sqlmodel import SQLModel, Field, create_engine

class Player(SQLModel, table=True):
    player_id: int = Field(primary_key=True)
    name: str | None = None
    age: int | None = None
    position: str | None = None
    team: str | None = None

class Stats(SQLModel, table=True):
    stat_id: int = Field(primary_key=True)
    
    # Foreign key linking to Player
    player_id: int = Field(foreign_key="player.player_id")
    name: str
    
    # NBA per-game stats
    ppg: float | None = None
    rpg: float | None = None
    apg: float | None = None
    fg_pct: float | None = None
    three_pt_pct: float | None = None
    spg: float | None = None
    bpg: float | None = None
    tov: float | None = None
    freethrow_pct: float | None = None


engine = create_engine("sqlite:///nba_2022-2023.db")
SQLModel.metadata.create_all(engine)