import csv
from typing import List, Dict
from sqlmodel import Session, select
from models import Stats, Player, engine
import unicodedata
import re
from difflib import get_close_matches


def _to_float(s: str):
    if s is None or s == '':
        return None
    try:
        return float(s)
    except ValueError:
        try:
            return float(s.replace('%', ''))
        except Exception:
            return None


def _normalize(name: str) -> str:
    # remove diacritics, punctuation, suffixes, and lowercase
    if not name:
        return ''
    n = unicodedata.normalize('NFKD', name)
    n = ''.join(ch for ch in n if not unicodedata.combining(ch))
    n = n.lower()
    # remove common suffixes like jr, sr, ii, iii, iv, v
    n = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", '', n)
    # remove punctuation
    n = re.sub(r"[^a-z0-9\s]", '', n)
    n = re.sub(r"\s+", ' ', n).strip()
    return n


def generate_stats_instances(session: Session | None = None) -> List[Stats]:
    """Read `stats.csv` and return a list of `Stats` instances.

    This function will attempt to match CSV `name` values to existing
    `Player.name` entries using normalized exact match and fuzzy matching.
    If no suitable match is found, it will create a new `Player` row.
    """
    close_session = False
    if session is None:
        session = Session(engine)
        close_session = True

    # build a mapping of normalized player names -> Player
    players: List[Player] = session.exec(select(Player)).all()
    norm_map: Dict[str, Player] = {}
    norms: List[str] = []
    for p in players:
        key = _normalize(p.name or '')
        if key:
            norm_map[key] = p
            norms.append(key)

    instances: List[Stats] = []
    with open('stats.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('name') or '').strip()
            if not name:
                continue

            norm = _normalize(name)
            player = None

            if norm in norm_map:
                player = norm_map[norm]
            else:
                # try fuzzy match
                if norms:
                    matches = get_close_matches(norm, norms, n=1, cutoff=0.85)
                    if matches:
                        player = norm_map[matches[0]]

            if player is None:
                # create missing player row (minimal info)
                player = Player(name=name)
                session.add(player)
                session.flush()
                # add to our mappings for future matches
                k = _normalize(player.name or '')
                if k:
                    norm_map[k] = player
                    norms.append(k)

            player_id = player.player_id

            stats = Stats(
                player_id=player_id,
                name=name,
                ppg=_to_float(row.get('ppg', '')),
                rpg=_to_float(row.get('rpg', '')),
                apg=_to_float(row.get('apg', '')),
                fg_pct=_to_float(row.get('fg_pct', '')),
                three_pt_pct=_to_float(row.get('three_pt_pct', '')),
                spg=_to_float(row.get('spg', '')),
                bpg=_to_float(row.get('bpg', '')),
                tov=_to_float(row.get('tov', '')),
                freethrow_pct=_to_float(row.get('freethrow_pct', '')),
            )
            instances.append(stats)

    if close_session:
        session.close()

    return instances
