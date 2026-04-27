"""Train doggo-flat with rsl_rl PPO.

Forwards every argument to Isaac Lab's stock
`scripts/reinforcement_learning/rsl_rl/train.py`, ensuring `doggo_tasks` is
imported first so the gym environment is registered.

Resolution order for Isaac Lab path:
  1. ISAACLAB_PATH environment variable.
  2. ~/IsaacLab.
  3. /opt/IsaacLab.

Usage:
    python scripts/train.py --task Isaac-Velocity-Flat-Doggo-v0 --headless --num_envs 4096
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
        if (c / "scripts" / "reinforcement_learning" / "rsl_rl" / "train.py").is_file():
            return c
    raise FileNotFoundError(
        "Could not locate Isaac Lab. Set ISAACLAB_PATH, e.g.\n"
        "    export ISAACLAB_PATH=/path/to/IsaacLab"
    )


ISAACLAB = _find_isaaclab()
ISAACLAB_TRAIN = ISAACLAB / "scripts" / "reinforcement_learning" / "rsl_rl" / "train.py"

# Default the task if user didn't pass --task.
if not any(a == "--task" or a.startswith("--task=") for a in sys.argv[1:]):
    sys.argv.insert(1, "--task")
    sys.argv.insert(2, "Isaac-Velocity-Flat-Doggo-v0")

# Make sure our tasks register before the train script calls gym.make.
import doggo_tasks  # noqa: F401

# Isaac Lab's train.py imports a sibling module (`cli_args`); add its dir to sys.path.
sys.path.insert(0, str(ISAACLAB_TRAIN.parent))

# Hand off as if invoked directly.
sys.argv[0] = str(ISAACLAB_TRAIN)
runpy.run_path(str(ISAACLAB_TRAIN), run_name="__main__")
