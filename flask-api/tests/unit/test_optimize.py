from optimize_core import FORMATION_MAP, SQUAD_LIMITS, optimize_squad


def _count_positions(players):
    counts = {"GK": 0, "DEF": 0, "MID": 0, "FWD": 0}
    for p in players:
        counts[p["position"]] = counts.get(p["position"], 0) + 1
    return counts


def test_optimize_respects_budget(sample_players):
    result = optimize_squad(sample_players, budget=80.0, formation="3-4-3")
    assert result["status"] == "optimal"
    selected = result["optimal_team"] + result["bench"]
    assert len(selected) == 15
    assert result["total_value"] <= 80.0 + 1e-6
    assert sum(p["value"] for p in selected) <= 80.0 + 1e-6


def test_optimize_formation_constraints(sample_players):
    formation = "4-3-3"
    result = optimize_squad(sample_players, budget=100.0, formation=formation)
    assert result["status"] == "optimal"

    squad = result["optimal_team"] + result["bench"]
    assert _count_positions(squad) == SQUAD_LIMITS
    assert _count_positions(result["optimal_team"]) == FORMATION_MAP[formation]
    assert len(result["optimal_team"]) == 11
    assert len(result["bench"]) == 4


def test_optimize_infeasible_tiny_budget(sample_players):
    result = optimize_squad(sample_players, budget=10.0, formation="3-4-3")
    assert result["status"] == "infeasible"
    assert result["optimal_team"] == []


def test_optimize_avoids_players(sample_players):
    avoid = [sample_players[0]["id"], sample_players[1]["id"]]
    result = optimize_squad(
        sample_players, budget=100.0, formation="3-4-3", avoid_players=avoid
    )
    assert result["status"] == "optimal"
    selected_ids = {p["id"] for p in result["optimal_team"] + result["bench"]}
    assert selected_ids.isdisjoint(set(avoid))
