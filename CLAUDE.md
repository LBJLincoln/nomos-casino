# Nomos Casino — Jeux Atari Addictifs + IA

> Repo autonome. Jeux retro addictifs avec IA qui optimise l'engagement.

## MISSION

Casino web avec jeux style Atari ultra-addictifs. L'IA analyse le comportement joueur
et ajuste la difficulte, les rewards, et le flow pour maximiser l'engagement.

## JEUX

| Jeu | Type | Status |
|-----|------|--------|
| **Breakout** | Atari classic — casser des briques | LIVE |
| **Crash** | Multiplicateur qui monte — cash out avant le crash | LIVE |
| **Snake** | Snake arcade — manger pour grandir | LIVE |
| **Slots** | Machine a sous retro-pixel | EXISTING |
| **Wheel** | Roue de fortune | EXISTING |
| **Pong** | Pong IA | PLANNED |

## ARCHITECTURE

```
Casino Page (Vercel) → Game Engine (Canvas/WebGL) → Score API → Leaderboard
                                                  ↓
                                           Engagement Tracker → IA Optimizer
```

## MECANIQUES ADDICTIVES (ethiques)
1. **Progression visible** — XP bar, niveaux, achievements
2. **Near-miss effect** — montrer ce qui a PRESQUE ete gagne
3. **Variable reward** — recompenses aleatoires (dopamine)
4. **Social proof** — leaderboard live
5. **Streak rewards** — bonus pour jeux consecutifs
6. **Sound design** — sons satisfaisants a chaque action

## EVAL TARGETS
- Time on page: > 3 min average
- Return rate: > 30% dans 7 jours
- Games played per session: > 5
- Score improvement: 10% par session

## COMMANDS
```bash
python3 agents/casino-tester.py --daemon 300     # Test continu
python3 tests/test-casino.py --all                # Test complet
python3 ops/sync.py                               # Sync vers mon-ipad
```
