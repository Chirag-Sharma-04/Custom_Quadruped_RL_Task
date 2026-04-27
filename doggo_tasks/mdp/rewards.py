"""Custom reward functions for the Doggo locomotion task.

These are added on top of Spot's reward set re-exported in this package's
`mdp/__init__.py`. Use these when you need a doggo-specific signal that the
Spot rewards don't already provide.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from isaaclab.assets import Articulation
from isaaclab.managers import SceneEntityCfg
from isaaclab.utils.math import quat_rotate_inverse

if TYPE_CHECKING:
    from isaaclab.envs import ManagerBasedRLEnv


def feet_lateral_distance_penalty(
    env: "ManagerBasedRLEnv",
    asset_cfg: SceneEntityCfg,
    threshold: float,
    body_y_offset: float = 0.0,
) -> torch.Tensor:
    """Penalize feet that swing across (or near) the body's sagittal plane.

    For each foot, computes the absolute lateral distance from the body
    centerline in the *body frame* (i.e. y-component after rotating the
    foot-relative-to-root vector by the inverse of root orientation). Feet
    whose lateral distance is less than `threshold` incur a quadratic penalty
    proportional to the shortfall.

    This is a direct geometric signal that bypasses joint-angle proxies, so
    it catches both hip-driven and knee-driven crossing — including the
    combined hip+knee compensation that satisfies per-joint penalties but
    still puts the foot near the centerline.

    Args:
        asset_cfg: SceneEntityCfg with `body_names` matching the foot bodies
            (e.g. `.*_foot`).
        threshold: minimum allowed |lateral| in meters. Reasonable starting
            values for doggo: 0.06–0.10. Smaller = more permissive.
        body_y_offset: y-distance (in body frame) from the body link's origin
            to the actual physical sagittal plane. Doggo's body link frame
            sits at the rear edge of the visual mesh and the CoM is offset
            by ~+0.099 m in y, so passing 0.099 here makes the penalty
            symmetric about the true centerline rather than the link origin.

    Returns:
        Tensor of shape (num_envs,) with sum-of-squared shortfall over feet.
    """
    asset: Articulation = env.scene[asset_cfg.name]

    # Foot positions in world frame: (num_envs, num_feet, 3)
    foot_pos_w = asset.data.body_pos_w[:, asset_cfg.body_ids, :]
    # Root pose
    root_pos_w = asset.data.root_pos_w.unsqueeze(1)        # (num_envs, 1, 3)
    root_quat_w = asset.data.root_quat_w                   # (num_envs, 4)

    # Translate to root, then rotate into body frame.
    foot_rel_w = foot_pos_w - root_pos_w                    # (num_envs, num_feet, 3)
    num_feet = foot_rel_w.shape[1]
    quat_b = root_quat_w.unsqueeze(1).expand(-1, num_feet, -1).reshape(-1, 4)
    vec_b = foot_rel_w.reshape(-1, 3)
    foot_pos_b = quat_rotate_inverse(quat_b, vec_b).reshape(-1, num_feet, 3)

    # Lateral distance from the *physical* sagittal plane: subtract the
    # link-origin-to-CoM offset so the penalty is symmetric about the true
    # centerline of the robot, not the link origin.
    lateral = (foot_pos_b[:, :, 1] - body_y_offset).abs()   # (num_envs, num_feet)
    # Quadratic penalty on shortfall below threshold.
    shortfall = torch.clamp(threshold - lateral, min=0.0)
    return shortfall.square().sum(dim=1)                    # (num_envs,)
