from sqlmodel import Session
from models import engine 
from players_instances import generate_players_instances

with Session(engine) as session:
    players = generate_players_instances()
    session.add_all(players)
    session.commit()