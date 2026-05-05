# Rules For Future LLM Sessions

Read this file first when working on this repo.

## Project Location

Repository:

- `/home/hp/IsaacLab/doggo_isaac_lab_task`

Previous extracted training logs/checkpoints:

- `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat`

## Bookkeeping Rules

Always keep these files updated:

- `README_LOG.md`: detailed chronological log.
- `README_TLDR.md`: short human-friendly conclusion summary.
- `README_LLM_RULES.md`: operating rules and durable instructions.

For each meaningful work session:

- Add an entry to `README_LOG.md` with exact date/time.
- Record what the user asked for.
- Record what files/commands were inspected or changed.
- Record important results, warnings, crashes, and decisions.
- If training output is provided, save the important metrics and interpretation.
- Update `README_TLDR.md` only with the current high-level conclusion.

Do not overwrite or delete earlier log entries. Append new entries. Do not log minor side details unless they affect future decisions, reproducibility, training interpretation, or deployment.

## User Preferences

- The user wants careful, durable progress tracking from now on.
- The user may paste training output several times; preserve it for future reference.
- Ignore zip files unless the user explicitly says otherwise.
- Explain conclusions clearly and practically.
- Ask questions only when needed; otherwise make reasonable engineering decisions.

## Codebase Rules

- Do not regenerate or replace `doggo_tasks/assets/doggo_v2.usd` unless the user explicitly asks.
- Do not enable robot self-collisions casually.
- Do not switch away from the current actuator model casually.
- Be careful with reward changes; compare visual behavior and metrics before changing weights.
- Preserve user changes and avoid unrelated refactors.
- Prefer small, inspectable edits.
- Use `rg`/`rg --files` for searching.
- Use `apply_patch` for manual file edits.

## Isaac Lab / Training Rules

- Main training env: `Isaac-Velocity-Flat-Doggo-v0`.
- Main play env: `Isaac-Velocity-Flat-Doggo-Play-v0`.
- Default RSL-RL experiment name: `doggo_flat`.
- Checkpoints live under `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat/<run>/`.
- Be aware that `drop_test.py` may fall back from `zero_agent.py` to `random_agent.py`; verify before treating it as a passive drop test.
- If Python imports behave oddly, check for ROS `PYTHONPATH` contamination. Isaac Sim Python worked previously with `PYTHONPATH` unset.

## Deployment Target Rules

- This policy is for Isaac Sim virtual deployment only, not a real physical robot.
- Do not bias decisions toward physical sim-to-real transfer unless the user explicitly changes the target.
- All actuators in deployment are expected to be Isaac Sim joints.
- Future deployment target may be Isaac Sim 4.5, 5.1, or 6.0; verify exact APIs and ROS 2 bridge details when a version is chosen.
- Desired deployment architecture: Doggo spawned in an Isaac Sim scene, Action Graph/ROS 2 bridge subscribes to joint commands, Isaac Sim publishes joint states, and optionally odometry/IMU.
- The trained policy should eventually run as a ROS 2 node.
- The ROS 2 policy node may eventually run on a Jetson Orin Nano Super, so keep runtime export/inference efficiency in mind.
- Keep training observations/actions aligned with the future deployment interface where practical.
- Track exactly what runtime inputs the policy needs before export: joint states, base orientation/gravity, base angular velocity, command velocity, last action, and any odometry/IMU assumptions.
- Policy outputs should be treated as desired joint position commands, not measured joint states.
- Deployment command conversion must reproduce training action scaling: `desired_joint_position = default_joint_position + 0.2 * policy_action`, unless the training action config changes.
- Isaac Sim should publish measured joint states; the ROS 2 policy node should publish desired joint commands on a separate command interface.
- Isaac Sim can provide both IMU and odometry. Use IMU for angular velocity/projected gravity and odometry for base linear velocity unless a future implementation chooses otherwise.
- Flat-ground walking is compulsory. Rough ground is secondary and should be introduced after stable flat-ground gait.
- Desired gait is Spot-like trot.

## Randomization Guidance

- Because deployment is sim-only, do not assume heavy sim-to-real randomization is required.
- Do not remove all randomization by default; Isaac Lab training and Isaac Sim deployment can still differ through friction, solver settings, timestep, scene contacts, command latency, and ROS 2 bridge timing.
- Prefer narrow randomization while learning the base gait.
- Consider reducing/disabling added base mass and push disturbances during early flat-ground gait training.
- Add rough terrain and stronger disturbances gradually after the flat trot is stable.

## Current Technical Hypothesis

The old reward setup trained better numerically but likely learned a criss-cross gait. The current setup adds geometric and posture penalties to prevent that, but optimization is harder and body-contact terminations are higher.

Before major reward edits, compare playback of:

- `2026-04-26_16-21-19/model_10850.pt`
- `2026-04-27_18-37-39/model_8100.pt`
- `2026-04-29_10-26-29/model_10650.pt`

Then decide whether to soften `joint_pos_hx`, soften `joint_pos_kn`, curriculum the lateral foot penalty, or adjust termination/reward balance.

Latest recommendation:

- Prefer the first successful reward/setup as the base for the next experiment.
- Add minimal anti-crossing logic first, especially direct `feet_lateral_distance`.
- Do not keep full-strength `joint_pos_hx` and `joint_pos_kn` by default during the next flat-ground retrain.
- Add hip/knee posture penalties only if visual playback shows they are necessary.
- Treat the second run's issues as likely over-constraint/too-much-difficulty-too-early, not proof that anti-crossing itself is wrong.

Current code state for next experiment:

- Stage-1 training uses plane terrain for flat-first learning.
- `feet_lateral_distance` is active at weight `-25.0`.
- Separate `joint_pos_hx` and `joint_pos_kn` reward terms are removed for now.
- General `joint_pos` penalty applies to all joints at weight `-0.7`.
- Friction, base mass randomization, and pushes are narrowed for easier gait learning.
- First test of this config should be a fresh run, not a resume from the second full-constraint checkpoint.
- Terrain-level curriculum is disabled for the plane-terrain stage.
- Viewer follows env 0's robot root with `origin_type="asset_root"`.

Latest completed run:

- Run folder: `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat/2026-05-04_18-25-16`
- Final checkpoint: `model_9999.pt`
- Stage-1 flat-ground run completed 10k iterations.
- Final mean reward was about `366`, peak mean reward was about `383`.
- Final mean episode length was about `961`.
- Final body-contact termination was about `5.4%`.
- Timeout termination was about `94.6%`.
- Terrain out-of-bounds was `0`.
- This run is numerically very strong for flat ground; do not change rewards again before reviewing videos/playback for gait quality and criss-cross behavior.
