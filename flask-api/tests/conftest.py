import os
import pytest

# Ensure deterministic token for decorator tests before app import side effects
os.environ.setdefault("INTERNAL_API_TOKEN", "test-internal-token")
os.environ.setdefault("DB_SSLMODE", "disable")
os.environ.setdefault("SECRET_KEY", "test-jwt-secret-not-for-production-use")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-not-for-production-use")


@pytest.fixture
def sample_players():
    """Synthetic 20-player pool covering all positions and multiple clubs."""
    players = []
    pid = 1
    clubs = ["ARS", "CHE", "LIV", "MCI", "TOT", "NEW", "BHA", "WHU"]
    for pos, count, base_value, base_pts in [
        ("GK", 4, 4.0, 40),
        ("DEF", 6, 4.0, 50),
        ("MID", 6, 4.5, 70),
        ("FWD", 4, 5.0, 80),
    ]:
        for i in range(count):
            players.append(
                {
                    "id": pid,
                    "name": f"{pos}_{i}",
                    "position": pos,
                    "team": clubs[(pid - 1) % len(clubs)],
                    "value": base_value + (i * 0.3),
                    "total_points": base_pts + i * 5,
                    "predicted_points": base_pts + i * 5 + 2,
                    "fplId": 1000 + pid,
                }
            )
            pid += 1
    return players
