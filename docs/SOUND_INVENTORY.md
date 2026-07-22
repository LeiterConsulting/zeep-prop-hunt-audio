# Sound inventory

Priority meanings:

- **P0:** required for the first playable public build.
- **P1:** important readability and variety immediately after the minimum pack.
- **P2:** polish or mode expansion.

## Positional world audio

| Priority | Event family | Target variants | Purpose |
| --- | --- | ---: | --- |
| P0 | `taunt.all.*` | 12-20 | Neutral vocal or nonverbal taunts for either role. |
| P0 | `taunt.prop.*` | 12-20 | Hiding, object, and discovery-themed taunts. |
| P0 | `taunt.hunter.*` | 8-12 | Search, suspicion, and pursuit-themed taunts. |
| P0 | `weapon.fire.*` | 3-5 | Hunter weapon shots. |
| P0 | `weapon.dry_fire.*` | 1-2 | Rejected/unavailable shot feedback. |
| P0 | `impact.prop.*` | 3-5 | Host-confirmed hit on a disguised player. |
| P0 | `impact.world.*` | 4-8 | Miss or scenery impact. |
| P0 | `player.prop_hurt.*` | 3-5 | Short damage reactions. |
| P0 | `player.eliminated.*` | 2-4 | Elimination at the player's position. |
| P0 | `disguise.apply.*` | 2-4 | Nearby transformation feedback. |
| P1 | `movement.prop_lock.*` | 1-2 | Orientation/position lock. |
| P1 | `movement.prop_unlock.*` | 1-2 | Return to free movement. |
| P1 | `footstep.hunter.*` | 6-10 | Only if suitable installed Zeepkist events cannot be invoked. |
| P1 | `footstep.prop.*` | 4-8 | Optional prop/object movement family. |
| P1 | `weapon.reload.*` | 2-3 | Only if final weapon design uses magazines. |
| P1 | `weapon.cooldown_ready.*` | 1-2 | Alternative for cooldown-based weapons. |
| P2 | `impact.wood.*` | 3-5 | Surface-specific miss. |
| P2 | `impact.metal.*` | 3-5 | Surface-specific miss. |
| P2 | `impact.plastic.*` | 3-5 | Surface-specific miss. |
| P2 | `impact.glass.*` | 3-5 | Surface-specific miss. |
| P2 | `prop.scrape.*` | 3-5 | Use only if repetition remains pleasant. |

## Local and interface audio

| Priority | Event family | Target variants | Purpose |
| --- | --- | ---: | --- |
| P0 | `ui.accept.*` | 1-2 | Valid action and selection. |
| P0 | `ui.back.*` | 1 | Cancel/back. |
| P0 | `ui.error.*` | 1-2 | Invalid action or content mismatch. |
| P0 | `ui.ready.*` | 1 | Enter ready state. |
| P0 | `ui.unready.*` | 1 | Leave ready state. |
| P0 | `disguise.preview.*` | 1 | Candidate selection. |
| P0 | `disguise.invalid.*` | 1 | Invalid disguise candidate. |
| P0 | `weapon.hit_confirm.*` | 1-2 | Played only after host validation. |
| P1 | `ui.player_join.*` | 1 | Lobby join. |
| P1 | `ui.player_leave.*` | 1 | Lobby departure. |
| P1 | `ui.countdown_tick.*` | 1-2 | Short countdown. |
| P1 | `ui.last_seconds_tick.*` | 1-2 | Urgent final countdown. |
| P2 | `ui.hover.*` | 1 | Subtle and rate-limited. |
| P2 | `ui.notification.*` | 1-2 | Generic information. |

## Round and match audio

| Priority | Event family | Target variants | Purpose |
| --- | --- | ---: | --- |
| P0 | `round.hiding_start.*` | 1 | Hiding phase begins. |
| P0 | `round.seeking_start.*` | 1 | Hunters are released. |
| P0 | `round.prop_win.*` | 1-2 | Props victory sting. |
| P0 | `round.hunter_win.*` | 1-2 | Hunters victory sting. |
| P0 | `round.local_eliminated.*` | 1 | Spectator transition. |
| P1 | `round.thirty_seconds.*` | 1 | Time warning. |
| P1 | `round.ten_seconds.*` | 1 | Final warning. |
| P1 | `round.last_prop.*` | 1 | Optional mode announcement. |
| P1 | `round.overtime.*` | 1 | If overtime is implemented. |
| P1 | `round.cancelled.*` | 1 | Session cannot continue. |
| P2 | `round.ambient_stinger.*` | 3-6 | Sparse non-positional tension cues. |

Every spoken announcement needs transcript and caption metadata. Before redistributing movement or environmental audio, determine whether an appropriate event can be invoked from the player's Zeepkist installation instead.

