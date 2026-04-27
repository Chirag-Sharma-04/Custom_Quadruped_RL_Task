"""Play (rollout) a trained doggo policy.

Resolution order for Isaac Lab path:
  1. ISAACLAB_PATH environment variable.
  2. ~/IsaacLab.
  3. /opt/IsaacLab.

Usage:
    python scripts/play.py --task Isaac-Velocity-Flat-Doggo-Play-v0 --num_envs 50
"""

import os
import runpy
import sys
from pathlib import Path


def _find_isaaclab() -> Path:
    candidates = []
    if "ISAACLAB_PATH" in os.environ:
        candidates.append(Path(os.environ["ISAACLAB_PATH"]))
    candidates += [Path.home() / "IsaacLab", Path("/opt/IsaacLab")]
    for c in candidates:
        if (c / "scripts" / "reinforcement_learning" / "rsl_rl" / "play.py").is_file():
            return c
    raise FileNotFoundError(
        "Could not locate Isaac Lab. Set ISAACLAB_PATH, e.g.\n"
        "    export ISAACLAB_PATH=/path/to/IsaacLab"
    )


ISAACLAB = _find_isaaclab()
ISAACLAB_PLAY = ISAACLAB / "scripts" / "reinforcement_learning" / "rsl_rl" / "play.py"

if not any(a == "--task" or a.startswith("--task=") for a in sys.argv[1:]):
    sys.argv.insert(1, "--task")
    sys.argv.insert(2, "Isaac-Velocity-Flat-Doggo-Play-v0")

import doggo_tasks  # noqa: F401

sys.path.insert(0, str(ISAACLAB_PLAY.parent))
sys.argv[0] = str(ISAACLAB_PLAY)
runpy.run_path(str(ISAACLAB_PLAY), run_name="__main__")
