"""Pure FPL squad optimization helpers (no Flask / network / model I/O)."""

from pulp import LpMaximize, LpProblem, LpVariable, lpSum

FORMATION_MAP = {
    "3-4-3": {"GK": 1, "DEF": 3, "MID": 4, "FWD": 3},
    "3-5-2": {"GK": 1, "DEF": 3, "MID": 5, "FWD": 2},
    "4-4-2": {"GK": 1, "DEF": 4, "MID": 4, "FWD": 2},
    "4-3-3": {"GK": 1, "DEF": 4, "MID": 3, "FWD": 3},
    "5-4-1": {"GK": 1, "DEF": 5, "MID": 4, "FWD": 1},
}

# Official FPL 15-man squad shape (formation applies only to starting XI split)
SQUAD_LIMITS = {"GK": 2, "DEF": 5, "MID": 5, "FWD": 3}


def get_formation_limits(formation: str) -> dict:
    return FORMATION_MAP.get(formation, FORMATION_MAP["3-4-3"])


def optimize_squad(
    players_data,
    budget=100.0,
    formation="3-4-3",
    locked_players=None,
    avoid_players=None,
    current_team=None,
    free_transfers=1,
):
    """
    Solve a 15-player FPL squad under budget / club / position rules.
    Formation is used when splitting starting XI vs bench after the solve.
    """
    locked_players = locked_players or []
    avoid_players = avoid_players or []
    current_team = current_team or []

    if avoid_players:
        avoid_ids = set(avoid_players)
        players_data = [p for p in players_data if p.get("id") not in avoid_ids]

    for player in players_data:
        if "predicted_points" not in player or player.get("predicted_points") is None:
            player["predicted_points"] = player.get("total_points", 0)

    position_limits = get_formation_limits(formation)

    problem = LpProblem("FPL_Team_Optimization", LpMaximize)
    player_vars = {
        player["id"]: LpVariable(f"player_{player['id']}", cat="Binary")
        for player in players_data
    }

    problem += lpSum(
        player_vars[player["id"]] * player.get("predicted_points", 0)
        for player in players_data
    )

    gk_players = [p for p in players_data if p.get("position") == "GK"]
    def_players = [p for p in players_data if p.get("position") == "DEF"]
    mid_players = [p for p in players_data if p.get("position") == "MID"]
    fwd_players = [p for p in players_data if p.get("position") == "FWD"]

    problem += lpSum(player_vars[p["id"]] for p in gk_players) == SQUAD_LIMITS["GK"]
    problem += lpSum(player_vars[p["id"]] for p in def_players) == SQUAD_LIMITS["DEF"]
    problem += lpSum(player_vars[p["id"]] for p in mid_players) == SQUAD_LIMITS["MID"]
    problem += lpSum(player_vars[p["id"]] for p in fwd_players) == SQUAD_LIMITS["FWD"]
    problem += lpSum(player_vars[player["id"]] for player in players_data) == 15
    problem += (
        lpSum(player_vars[player["id"]] * player.get("value", 0) for player in players_data)
        <= budget
    )

    for team in {p.get("team", "") for p in players_data}:
        if not team:
            continue
        team_players = [p for p in players_data if p.get("team") == team]
        problem += lpSum(player_vars[p["id"]] for p in team_players) <= 3

    for player_id in locked_players:
        if player_id in player_vars:
            problem += player_vars[player_id] == 1

    status = problem.solve()
    if status != 1:  # LpStatusOptimal
        return {
            "optimal_team": [],
            "bench": [],
            "captain": None,
            "vice_captain": None,
            "transfers": [],
            "total_value": 0.0,
            "total_points": 0,
            "formation": formation,
            "status": "infeasible",
        }

    selected_players = [
        player
        for player in players_data
        if player_vars[player["id"]].varValue and player_vars[player["id"]].varValue > 0.5
    ]
    selected_players.sort(
        key=lambda x: x.get("predicted_points", x.get("total_points", 0)),
        reverse=True,
    )

    optimal_team = []
    bench = []
    position_counts = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}

    for player in selected_players:
        pos = player.get("position", "")
        if pos in position_counts and position_counts[pos] < position_limits[pos]:
            optimal_team.append(player)
            position_counts[pos] += 1
        elif len(bench) < 4:
            bench.append(player)

    captain = (
        max(optimal_team, key=lambda x: x.get("predicted_points", x.get("total_points", 0)))
        if optimal_team
        else None
    )
    vice_captain = None
    if optimal_team and captain:
        others = [p for p in optimal_team if p.get("id") != captain.get("id")]
        vice_captain = (
            max(others, key=lambda x: x.get("predicted_points", x.get("total_points", 0)))
            if others
            else captain
        )

    transfers = []
    if free_transfers > 0 and current_team:
        current_team_sorted = sorted(current_team, key=lambda x: x.get("total_points", 0))
        for i in range(min(free_transfers, len(current_team_sorted))):
            player_out = current_team_sorted[i]
            better_players = [
                p
                for p in optimal_team
                if p.get("position") == player_out.get("position")
                and p.get("predicted_points", p.get("total_points", 0))
                > player_out.get("total_points", 0)
            ]
            if better_players:
                player_in = better_players[0]
                transfers.append(
                    {
                        "player_out": player_out,
                        "player_in": player_in,
                        "cost": player_in.get("value", 0) - player_out.get("value", 0),
                        "reason": (
                            f"Upgrade from {player_out.get('total_points', 0)} to "
                            f"{player_in.get('predicted_points', player_in.get('total_points', 0))} "
                            "predicted points"
                        ),
                    }
                )

    total_value = sum(p.get("value", 0) for p in selected_players)
    total_points = sum(
        p.get("predicted_points", p.get("total_points", 0)) for p in optimal_team
    )

    return {
        "optimal_team": optimal_team,
        "bench": bench,
        "captain": captain,
        "vice_captain": vice_captain,
        "transfers": transfers,
        "total_value": total_value,
        "total_points": int(total_points),
        "formation": formation,
        "status": "optimal",
    }
