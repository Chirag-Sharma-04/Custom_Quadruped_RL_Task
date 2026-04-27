"""Articulation config for the Doggo quadruped.

Doggo is a custom 12-DoF quadruped (4 legs × {hx, hy, kn}). Body and leg link
names mirror Spot conventions so the same regexes (`.*_h[xy]`, `.*_kn`, `body`,
`.*_foot`, `.*leg`) used in Isaac Lab's locomotion-velocity task work without
modification.

USD asset resolution order:
  1. `DOGGO_USD_PATH` environment variable, if set.
  2. `<package_root>/doggo_tasks/assets/doggo_v2.usd` (bundled with this package).
"""

import os
from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.actuators import DelayedPDActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

_PKG_ROOT = Path(__file__).resolve().parent
_BUNDLED_USD = _PKG_ROOT / "assets" / "doggo_v2.usd"

DOGGO_USD_PATH: str = os.environ.get("DOGGO_USD_PATH", str(_BUNDLED_USD))

if not Path(DOGGO_USD_PATH).is_file():
    raise FileNotFoundError(
        f"Doggo USD not found at {DOGGO_USD_PATH!r}. "
        "Either set DOGGO_USD_PATH to your USD path, or place the USD at "
        f"{_BUNDLED_USD}."
    )


DOGGO_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=DOGGO_USD_PATH,
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=32,
            solver_velocity_iteration_count=1,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        # Body center sits ~0.626 m above feet at rest; a small extra clearance
        # gives the policy a clean drop-in without intersecting the ground.
        pos=(0.0, 0.0, 0.65),
        joint_pos={
            # Wider stance to discourage feet crossing the body centerline (~11.5°).
            "[fh]l_hx": 0.2,
            "[fh]r_hx": -0.2,
            # Front and hind hip-y flexed forward (Spot-style); inside doggo's
            # tightened hy range [-0.899, 2.295].
            "f[rl]_hy": 0.9,
            "h[rl]_hy": 1.1,
            # Knees bent. doggo's kn range is [-2.793, -0.247]; -1.5 is well inside.
            ".*_kn": -1.5,
        },
        joint_vel={".*": 0.0},
    ),
    actuators={
        # All 12 joints share the same delayed-PD actuator. Spot's spec uses a
        # remotized actuator for the knee because of its 4-bar transmission;
        # doggo's knee is a direct revolute, so a plain DelayedPDActuator is
        # the correct match.
        "doggo_legs": DelayedPDActuatorCfg(
            joint_names_expr=[".*_h[xy]", ".*_kn"],
            effort_limit=100.0,
            velocity_limit=20.0,
            stiffness=60.0,
            damping=1.5,
            min_delay=0,  # min: 0 ms
            max_delay=4,  # max: 4 * 2 ms = 8 ms
        ),
    },
)
"""Configuration for the Doggo quadruped robot (flat-locomotion ready)."""
