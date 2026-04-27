# CLAUDE_HANDOFF.md

> Hi Claude. The user is moving this Isaac Lab training package from another
> system to this one. They expect you to read this file, understand the setup,
> verify the prerequisites, and get them to a working `train.py` invocation
> with minimal back-and-forth.

## What this package is

A standalone Isaac Lab task for training a custom 12-DoF quadruped called
**doggo** with PPO (rsl_rl or skrl). It's modeled on Boston Dynamics' Spot
Flat task — same observations, rewards, terminations, terrain, sim rates —
with three doggo-specific changes (`DelayedPDActuatorCfg` for knees,
self-collisions disabled, init body height 0.65 m).

The USD asset (`doggo_tasks/assets/doggo_v2.usd`, ~3 MB) is **fully
self-contained**: no Nucleus refs, no external meshes, no payloads. It was
authored from a URDF and post-processed extensively (foot rigid bodies, sphere
colliders, contact-report APIs, MDL materials, articulation iters=32, drive
K=60 D=1.5).

The user has been told the USD passes 20/20 readiness checks, so don't
re-litigate that unless they ask. Believe the file is ready.

## Setup checklist (do these in order)

### 1. Verify Isaac Lab is installed and works for Spot

Before doggo-specific work, confirm Isaac Lab itself runs. Ask the user
where Isaac Lab is, or check the usual locations:
```bash
ls ~/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py
ls /opt/IsaacLab/scripts/reinforcement_learning/rsl_rl/train.py
echo "$ISAACLAB_PATH"
```

Run Spot's training for 5 iterations as a smoke test (the user already trusts
this works on the source system; here it confirms the new system is set up):
```bash
cd ~/IsaacLab && ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Spot-v0 --headless --num_envs 64 --max_iterations 5
```
If this fails, fix Isaac Lab first — none of the doggo work matters until
this works. Common fixes:
- `pip install rsl-rl-lib` if rsl_rl missing
- `./isaaclab.sh --install rsl_rl` (Isaac Lab's installer)
- Source ROS *after* Isaac Lab's env if ROS is sourced (ROS leaks Python 3.10
  paths into a 3.11 env and breaks `numpy`/`gymnasium` imports)

### 2. Set ISAACLAB_PATH if Isaac Lab isn't at `~/IsaacLab`

```bash
export ISAACLAB_PATH=/actual/path/to/IsaacLab
```

The wrapper scripts in `scripts/train.py`, `scripts/play.py`,
`scripts/drop_test.py` look up `ISAACLAB_PATH` first, then fall back to
`~/IsaacLab` and `/opt/IsaacLab`.

### 3. Install this package (editable)

From this directory:
```bash
~/IsaacLab/_isaac_sim/python.sh -m pip install -e .
```
…or whatever Python actually has Isaac Lab on its path. To verify:
```bash
~/IsaacLab/_isaac_sim/python.sh -c "import doggo_tasks; print('OK')"
```

If that fails with `No module named 'gymnasium'` or `'numpy'` despite Isaac
Lab being installed, the user's shell has ROS sourced and is poisoning
`sys.path`. Run `unset PYTHONPATH` before re-trying. Document this for the
user.

### 4. Smoke-test the registration

```bash
~/IsaacLab/isaaclab.sh -p -c "
import doggo_tasks
import gymnasium as gym
ids = sorted(s for s in gym.registry.keys() if 'Doggo' in s)
print('Registered:', ids)
print('USD:', doggo_tasks.doggo_cfg.DOGGO_USD_PATH)
"
```
Expected output:
```
Registered: ['Isaac-Velocity-Flat-Doggo-Play-v0', 'Isaac-Velocity-Flat-Doggo-v0']
USD: /.../doggo_tasks/assets/doggo_v2.usd
```

### 5. Drop test (does the robot stand at init pose?)

This is the **most important pre-training check**. The init joint pose was
borrowed from Spot and may need tuning for doggo's leg geometry.

```bash
~/IsaacLab/isaaclab.sh -p scripts/drop_test.py --num_envs 1
```

Watch for ~3 seconds. **Pass:** robot quivers but stays roughly upright.
**Fail:** robot collapses to one side or face-plants immediately.

If it fails, edit `doggo_tasks/doggo_cfg.py` → `DOGGO_CFG.init_state.joint_pos`.
The defaults are Spot's (front hy=0.9, hind hy=1.1, kn=-1.5, hx=±0.1).
Common adjustments:
- Robot lands on belly → `kn` more negative (e.g. -1.8) to bend knees more
- Robot toppled forward → reduce front `hy` (e.g. 0.7)
- Robot toppled backward → increase front `hy` or reduce hind `hy`
- Hips splayed too wide → reduce |hx|

Iterate the drop test until the robot stands.

### 6. Short training run (200 iters, ~10 min)

```bash
~/IsaacLab/isaaclab.sh -p scripts/train.py \
    --task Isaac-Velocity-Flat-Doggo-v0 \
    --headless --num_envs 1024 --max_iterations 200
```

Watch the rsl_rl log:
- **Mean reward** should trend upward (not necessarily monotonic)
- **Mean episode length** should be > the minimum after ~50 iters
- If reward is flat at -100 or episodes always terminate at step 1, the body
  is contacting the ground at spawn — increase `init_state.pos[2]` (default
  0.65 m) by 0.05 m at a time

### 7. Full training

```bash
~/IsaacLab/isaaclab.sh -p scripts/train.py \
    --task Isaac-Velocity-Flat-Doggo-v0 \
    --headless --num_envs 4096
```

20 000 iterations is the default in `rsl_rl_ppo_cfg.py`. On a 4090 this is
roughly 2-4 hours.

## Files transferred (verify these exist after copy)

```
doggo_isaac_lab_task/
├── pyproject.toml
├── README.md
├── CLAUDE_HANDOFF.md
├── doggo_tasks/
│   ├── __init__.py
│   ├── doggo_cfg.py
│   ├── flat_env_cfg.py
│   ├── assets/
│   │   └── doggo_v2.usd               ★ ~3 MB, must be present
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── rsl_rl_ppo_cfg.py
│   │   └── skrl_flat_ppo_cfg.yaml
│   └── mdp/
│       └── __init__.py
└── scripts/
    ├── train.py
    ├── play.py
    └── drop_test.py
```

Quick check:
```bash
test -s doggo_tasks/assets/doggo_v2.usd && echo "USD present" || echo "MISSING"
find . -name "*.py" -exec python3 -m py_compile {} \;
echo "All compile checks done"
```

## Things you should NOT do without asking

- **Don't regenerate the USD from URDF.** The USD has manual fixes (foot rigid
  bodies, sphere colliders, MDL material bindings, drive K/D, articulation
  iters) that won't survive a fresh URDF→USD import. The URDF is at
  `/home/chirag/robot_doggo/doggo_v2.urdf` on the source system but isn't
  required at runtime — don't include it unless the user asks.
- **Don't change the reward weights** in `flat_env_cfg.py:DoggoRewardsCfg`
  unless the user reports a specific failure mode (e.g. "robot hops, doesn't
  walk"). The Spot reward set is well-tuned.
- **Don't switch the actuator type** to `RemotizedPDActuatorCfg`. Doggo's
  knee is a direct revolute, not a 4-bar — the lookup table doesn't apply.
- **Don't enable self-collisions** at the articulation level. Doggo's USD
  has no per-link collision-filter pairs; enabling self-collisions causes
  spurious adjacent-link contacts (hip↔body, uleg↔hip).

## Things you can do without asking

- Adjust `init_state.joint_pos` in `doggo_cfg.py` based on drop-test results.
- Adjust `init_state.pos[2]` (body height) if drop test shows ground contact.
- Re-run drop tests, smoke training, full training.
- Set `ISAACLAB_PATH` and `DOGGO_USD_PATH` env vars.
- `pip install -e .` (idempotent).

## Known design choices and quirks

- **Body link frame is at the rear edge** of the visual mesh, so body CoM is
  offset Y≈+0.099 m. Trainable; don't try to "fix" by shifting the body in
  the USD without also re-authoring all the joint origins.
- **Foot mass is 50 g** with sphere inertia (8e-6 kg·m²) — light but
  numerically stable. Earlier values of 1µg with zero inertia produced -inf
  CoM and crashed PhysX, hence the bump.
- **Joint limits are Spot-tight** in v2 (hx ±45°, hy [-51.5°, 131.5°],
  kn [-160°, -14.2°]). A wider-limits v1 USD/URDF exists at
  `/home/chirag/Documents/Isaac_Stuff/Doggo/doggo.usd` and
  `/home/chirag/robot_doggo/doggo.urdf` on the source system as a fallback if
  the policy can't fit a gait inside v2's range.

## If training totally fails

Most likely causes, in order:
1. **Init pose puts robot off-balance.** Drop test catches this. Fix in
   `doggo_cfg.py:DOGGO_CFG.init_state.joint_pos`.
2. **Body height too low; ground contact at spawn.** Bump
   `init_state.pos[2]` from 0.65 to 0.70.
3. **CAD-derived inertias are wildly off.** Symptoms: robot trains but
   converges to weird hopping gait. Edit URDF inertials and re-import (heavy
   lift — only do if other fixes don't work).
4. **Doggo's joint axis sign convention differs from Spot's.** Symptoms:
   init pose is mirrored / inverted. Flip signs in `init_state.joint_pos`
   (e.g. negate the `hy` values).

Document any iteration the user does so they have a trail to refer back to.

— end of handoff —
