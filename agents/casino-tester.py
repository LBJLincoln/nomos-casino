#!/usr/bin/env python3
"""
Casino Tester — Autonomous testing of casino games and engagement.
Tests game loading, API response, scoring system, and user experience.
"""

import os, sys, json, time, random, ssl, traceback, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent

def load_env():
    env_file = ROOT / ".env.local"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:]
            if "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))

load_env()

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

CASINO_URL = "https://nomos42.vercel.app/casino"

# ── User personas ─────────────────────────────────────────────────────────────
PERSONAS = [
    {"id": "casual-gamer", "style": "Quick sessions, low stakes, prefers simple games"},
    {"id": "high-roller", "style": "Aggressive bets, loves crash game, chases multipliers"},
    {"id": "retro-fan", "style": "Loves Atari classics, Breakout addict, pixel art lover"},
    {"id": "competitive", "style": "Score-focused, leaderboard hunter, plays daily"},
    {"id": "mobile-user", "style": "Phone browser, touch controls, short attention span"},
    {"id": "streamer", "style": "Playing for audience, needs visual excitement"},
]

# ── Test scenarios ────────────────────────────────────────────────────────────
GAME_TESTS = [
    {"game": "breakout", "checks": ["canvas_render", "paddle_control", "brick_collision", "score_update", "level_progression"]},
    {"game": "crash", "checks": ["multiplier_growth", "cash_out", "auto_crash", "history_display", "bet_validation"]},
    {"game": "snake", "checks": ["movement", "food_spawn", "growth", "wall_collision", "score_tracking"]},
    {"game": "slots", "checks": ["reel_spin", "symbol_match", "payout_calc", "animation", "sound"]},
    {"game": "wheel", "checks": ["spin_animation", "prize_landing", "prize_display", "history"]},
]

# ── Persona → preferred games ────────────────────────────────────────────────
PERSONA_GAMES = {
    "casual-gamer": ["slots", "wheel"],
    "high-roller": ["crash", "slots"],
    "retro-fan": ["breakout", "snake"],
    "competitive": ["breakout", "snake"],
    "mobile-user": ["slots", "wheel", "snake"],
    "streamer": ["crash", "breakout"],
}

# ── HTML markers proving each game is present ────────────────────────────────
GAME_MARKERS = {
    "breakout": ["breakout", "brick", "paddle"],
    "crash": ["crash", "multiplier", "cash"],
    "snake": ["snake"],
    "slots": ["slot", "spin", "reel"],
    "wheel": ["wheel", "prize"],
}

def _fetch_page():
    """Fetch casino page HTML. Returns (html, status) or raises."""
    req = urllib.request.Request(CASINO_URL)
    with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace"), resp.status

def test_page_load():
    """Test casino page loads correctly."""
    try:
        req = urllib.request.Request(CASINO_URL)
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            html = resp.read().decode("utf-8")
            status = resp.status

            checks = {
                "status_200": status == 200,
                "has_casino_content": "casino" in html.lower() or "NOMOS" in html,
                "has_game_elements": any(g in html.lower() for g in ["breakout", "crash", "snake", "slots", "wheel", "canvas"]),
                "page_size_ok": len(html) > 5000,
                "has_scripts": "<script" in html,
            }

            passed = sum(1 for v in checks.values() if v)
            total = len(checks)

            return {
                "test": "page_load",
                "passed": passed == total,
                "score": passed / total * 100,
                "checks": checks,
                "page_size": len(html),
                "status": status,
            }
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        return {"test": "page_load", "passed": False, "score": 0, "error": f"{type(e).__name__}: {e}"}

def test_engagement_metrics(html):
    """Validate engagement features against actual page content."""
    h = html.lower()

    engagement_checks = {
        "has_progression_system": any(w in h for w in ["xp", "level", "score", "point", "achievement"]),
        "has_variable_rewards": any(w in h for w in ["bonus", "reward", "prize", "jackpot", "random"]),
        "has_sound_design": any(w in h for w in ["audio", "sound", ".mp3", ".wav", "howl"]),
        "has_visual_feedback": any(w in h for w in ["canvas", "animation", "particle", "glow", "neon"]),
        "has_leaderboard": any(w in h for w in ["leaderboard", "ranking", "top score", "highscore"]),
        "has_streak_rewards": any(w in h for w in ["streak", "consecutive", "daily", "combo"]),
        "has_near_miss_effect": any(w in h for w in ["near", "almost", "close", "miss"]),
        "has_quick_restart": any(w in h for w in ["restart", "retry", "play again", "new game"]),
        "has_difficulty_curve": any(w in h for w in ["level", "difficulty", "stage", "wave"]),
        "has_mobile_support": any(w in h for w in ["mobile", "touch", "responsive", "viewport"]),
    }

    score = sum(1 for v in engagement_checks.values() if v) / len(engagement_checks) * 100

    return {
        "test": "engagement_design",
        "passed": score >= 50,
        "score": round(score, 1),
        "checks": engagement_checks,
    }

def test_game_content(html, persona):
    """Validate game presence with persona-weighted scoring using GAME_TESTS."""
    h = html.lower()
    preferred = PERSONA_GAMES.get(persona["id"], ["breakout"])

    game_results = {}
    for game_test in GAME_TESTS:
        game = game_test["game"]
        markers = GAME_MARKERS.get(game, [game])
        found = [m for m in markers if m in h]
        game_results[game] = {
            "present": len(found) > 0,
            "markers_found": found,
            "is_preferred": game in preferred,
        }

    # Preferred games weigh 2x
    total_weight = 0
    earned = 0
    for game, result in game_results.items():
        weight = 2 if result["is_preferred"] else 1
        total_weight += weight
        if result["present"]:
            earned += weight

    score = (earned / total_weight * 100) if total_weight > 0 else 0

    return {
        "test": "game_content",
        "passed": score >= 60,
        "score": round(score, 1),
        "persona": persona["id"],
        "preferred_games": preferred,
        "games": game_results,
    }

def run_cycle(cycle_num):
    """Run a full test cycle."""
    ts = datetime.now(timezone.utc).isoformat()[:19]
    persona = random.choice(PERSONAS)

    print(f"\n[CYCLE {cycle_num}] Persona: {persona['id']} — {ts}")

    results = []

    # Fetch page once, share HTML across tests
    html = None
    print("  Testing page load...")
    page_result = test_page_load()
    results.append(page_result)
    print(f"    Page load: {'PASS' if page_result['passed'] else 'FAIL'} ({page_result['score']:.0f}%)")

    # Fetch HTML for content-based tests
    if page_result["passed"]:
        try:
            html, _ = _fetch_page()
        except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
            print(f"    [WARN] Failed to fetch page for content tests: {e}")
            html = None

    # Test game content (uses GAME_TESTS + persona preference)
    if html:
        print(f"  Testing game content for {persona['id']}...")
        game_result = test_game_content(html, persona)
        results.append(game_result)
        print(f"    Game content: {'PASS' if game_result['passed'] else 'FAIL'} ({game_result['score']:.0f}%)")

    # Test engagement design (real HTML checks)
    if html:
        print("  Testing engagement design...")
        engagement_result = test_engagement_metrics(html)
        results.append(engagement_result)
        print(f"    Engagement: {'PASS' if engagement_result['passed'] else 'FAIL'} ({engagement_result['score']:.0f}%)")
    else:
        print("  Skipping content tests (page not available)")

    # Overall score
    if not results:
        print("  No test results collected — skipping cycle summary")
        return {"cycle": cycle_num, "timestamp": ts, "persona": persona["id"], "overall_score": 0, "passed": False, "results": []}
    avg_score = sum(r["score"] for r in results) / len(results)
    passed = all(r["passed"] for r in results)

    # Log results
    log_entry = {
        "cycle": cycle_num,
        "timestamp": ts,
        "persona": persona["id"],
        "overall_score": round(avg_score, 1),
        "passed": passed,
        "results": results,
    }

    metrics_file = ROOT / "logs" / "metrics.jsonl"
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(metrics_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    except OSError as e:
        print(f"  [WARN] Could not write metrics log: {e}")

    # Sync to mon-ipad
    try:
        sync_dir = Path("/home/termius/mon-ipad/data/casino")
        sync_dir.mkdir(parents=True, exist_ok=True)
        (sync_dir / "latest-test.json").write_text(json.dumps(log_entry, indent=2))
    except OSError as e:
        print(f"  [WARN] Sync to mon-ipad failed: {e}")

    print(f"  Overall: {'PASS' if passed else 'FAIL'} ({avg_score:.0f}%)")

    return log_entry

def daemon_loop(interval=300):
    """Continuous testing loop."""
    cycle = 0
    print(f"Casino Tester daemon started — testing every {interval}s")

    try:
        while True:
            cycle += 1
            try:
                run_cycle(cycle)
            except Exception as e:
                print(f"[ERROR] Cycle {cycle}: {e}")
                try:
                    err_file = ROOT / "logs" / "errors.jsonl"
                    err_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(err_file, "a") as f:
                        f.write(json.dumps({"cycle": cycle, "error": str(e), "traceback": traceback.format_exc(), "ts": datetime.now(timezone.utc).isoformat()}) + "\n")
                except OSError as log_err:
                    print(f"  [WARN] Could not write error log: {log_err}")

            print(f"  Sleeping {interval}s...")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\nDaemon stopped after {cycle} cycles.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Casino Tester")
    parser.add_argument("--daemon", type=int, metavar="INTERVAL", help="Daemon mode")
    parser.add_argument("--once", action="store_true", help="Run once")
    args = parser.parse_args()

    if args.daemon:
        daemon_loop(args.daemon)
    else:
        run_cycle(1)
