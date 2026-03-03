from sqlmodel import Session
from models import engine, Stats
from stats_instances import generate_stats_instances

with Session(engine) as session:
    stats = generate_stats_instances()
    for s in stats:
        session.merge(s)
    session.commit()