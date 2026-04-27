"""MDP terms for the Doggo locomotion task.

We re-export Spot's locomotion mdp module verbatim — the reward and event
functions there are written against generic body-name regexes (`.*_foot`,
`body`, etc.) that Doggo also uses.

If you want to customize a reward or event for Doggo specifically, drop a new
function into events.py / rewards.py and update the import below.
"""

from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp.events import *  # noqa: F401, F403
from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp.rewards import *  # noqa: F401, F403

# Doggo-specific reward terms (override or extend the Spot defaults).
from .rewards import feet_lateral_distance_penalty  # noqa: F401
