import csv
from typing import List
from sqlmodel import Session
from models import Player, engine


def _to_int(s: str):
    if s is None or s == '':
        return None
    try:
        return int(float(s))
    except Exception:
        return None


def generate_players_instances(session: Session | None = None) -> List[Player]:
    """Read `players.csv` and return a list of `Player` instances.

    The function accepts an optional `session` but does not require it.
    """
    close_session = False
    if session is None:
        session = Session(engine)
        close_session = True

    instances: List[Player] = []
    with open('players.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', '').strip()
            if not name:
                continue
            age = _to_int(row.get('age', '').strip())
            position = row.get('position', '').strip() or None
            team = row.get('team', '').strip() or None

            player = Player(
                name=name,
                age=age,
                position=position,
                team=team,
            )
            instances.append(player)

    if close_session:
        session.close()

    return instances
