"""Drop-test sanity: spawn doggo with NO policy actions, just gravity.

Run this first on a new system to confirm the robot stands up at the
init pose. If it collapses, the init joint_pos in doggo_cfg.py needs tuning.

Usage:
    python scripts/drop_test.py --num_envs 1
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
    raise FileNotFoundError("Set ISAACLAB_PATH to your IsaacLab install.")


ISAACLAB = _find_isaaclab()

# Reuse Isaac Lab's environments.py for headless verification.
# We run the play env config but without loading a policy — just step zeros.
ISAACLAB_TEST = ISAACLAB / "scripts" / "environments" / "zero_agent.py"
if not ISAACLAB_TEST.is_file():
    # Fallback to play.py with a dummy --checkpoint that won't be loaded if we
    # short-circuit, but Isaac Lab's play requires a policy. Use random_agent.
    ISAACLAB_TEST = ISAACLAB / "scripts" / "environments" / "random_agent.py"

if not any(a == "--task" or a.startswith("--task=") for a in sys.argv[1:]):
    sys.argv.insert(1, "--task")
    sys.argv.insert(2, "Isaac-Velocity-Flat-Doggo-Play-v0")

import doggo_tasks  # noqa: F401

print(f"[drop_test] Using IsaacLab at: {ISAACLAB}")
print(f"[drop_test] Running: {ISAACLAB_TEST}")
sys.path.insert(0, str(ISAACLAB_TEST.parent))
sys.argv[0] = str(ISAACLAB_TEST)
runpy.run_path(str(ISAACLAB_TEST), run_name="__main__")
