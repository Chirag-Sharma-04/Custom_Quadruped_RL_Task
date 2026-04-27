# Doggo — Isaac Lab Locomotion Task

Standalone Isaac Lab task package for the **Doggo** quadruped, modeled on
Boston Dynamics' Spot Flat task with three doggo-specific changes
(actuator type, self-collisions, init body height).

## What's in this package

```
doggo_isaac_lab_task/
├── pyproject.toml                                 (pip-installable)
├── README.md                                      (this file)
├── CLAUDE_HANDOFF.md                              (instructions for Claude on a new machine)
├── doggo_tasks/
│   ├── __init__.py                                gym.register
│   ├── doggo_cfg.py                               DOGGO_CFG ArticulationCfg
│   ├── flat_env_cfg.py                            DoggoFlatEnvCfg + _PLAY variant
│   ├── assets/
│   │   └── doggo_v2.usd                           ★ the rock-solid training asset (3 MB)
│   ├── agents/
│   │   ├── rsl_rl_ppo_cfg.py                      DoggoFlatPPORunnerCfg
│   │   └── skrl_flat_ppo_cfg.yaml                 skrl PPO config
│   └── mdp/
│       └── __init__.py                            re-exports Spot's events + rewards
└── scripts/
    ├── train.py                                   wrapper around IsaacLab's train.py
    ├── play.py                                    wrapper around IsaacLab's play.py
    └── drop_test.py                               sanity: spawn doggo with no policy
```

The USD `doggo_tasks/assets/doggo_v2.usd` is **fully self-contained** (no external
mesh files, no Nucleus dependencies). The package is plug-and-play once Isaac
Lab is installed.

## Prerequisites

- Isaac Sim 4.5 (or compatible) installed
- Isaac Lab installed (e.g. `~/IsaacLab` with editable install in your conda env)
- A working `isaaclab.sh -p` invocation that runs Python with all RL deps
  (`gymnasium`, `numpy`, `torch`, `rsl_rl`, `isaaclab*`)

If you can run Isaac Lab's stock Spot training:
```bash
cd ~/IsaacLab && ./isaaclab.sh -p scripts/reinforcement_learning/rsl_rl/train.py \
    --task Isaac-Velocity-Flat-Spot-v0 --headless --num_envs 64 --max_iterations 5
```
…then this package will work the same way.

## Install

From the directory containing this README:
```bash
~/IsaacLab/_isaac_sim/python.sh -m pip install -e .
```
or use whatever Python invokes Isaac Lab on your system. The `-e` (editable)
install means changes to the source files take effect immediately.

## Train

```bash
# Default 4096 envs, 20 000 iters (~few hours on a 4090).
~/IsaacLab/isaaclab.sh -p scripts/train.py \
    --task Isaac-Velocity-Flat-Doggo-v0 \
    --headless --num_envs 4096
```

The first run will print:
```
Registered doggo envs: ['Isaac-Velocity-Flat-Doggo-Play-v0', 'Isaac-Velocity-Flat-Doggo-v0']
```

Logs / checkpoints land in `~/IsaacLab/logs/rsl_rl/doggo_flat/<timestamp>/`.

## Play (rollout a trained policy)

```bash
~/IsaacLab/isaaclab.sh -p scripts/play.py \
    --task Isaac-Velocity-Flat-Doggo-Play-v0 --num_envs 50
```

Pass `--checkpoint <path>` to load a specific checkpoint, or omit it to use the
latest run.

## Sanity-check before committing to a long training run

**Strongly recommended.** Run a short 200-iteration training to confirm
nothing's catastrophically wrong:
```bash
~/IsaacLab/isaaclab.sh -p scripts/train.py \
    --task Isaac-Velocity-Flat-Doggo-v0 \
    --headless --num_envs 1024 --max_iterations 200
```
If `Mean reward` trends upward and `Mean episode length` doesn't stay at the
minimum, you're good to scale up.

## Differences vs Spot Flat

| What | Spot | Doggo |
|---|---|---|
| Knee actuator | `RemotizedPDActuatorCfg` w/ joint-parameter lookup (4-bar transmission) | `DelayedPDActuatorCfg` (direct revolute) |
| Self-collisions | `True` | `False` (USD has no inter-link collision filters) |
| Init body height | 0.5 m | 0.65 m |
| Robot asset | Spot USD on Nucleus | bundled `doggo_tasks/assets/doggo_v2.usd` |

Everything else (observations, actions, commands, rewards, terminations,
randomization, terrain, sim rates) is identical to Spot Flat.

## Customizing

- **Reward weights / new rewards** → `flat_env_cfg.py:DoggoRewardsCfg`
- **Init pose** → `doggo_cfg.py:DOGGO_CFG.init_state.joint_pos`
- **Actuator gains** → `doggo_cfg.py:DOGGO_CFG.actuators["doggo_legs"]`
  (currently K=60, D=1.5, eff=100 N·m, vel=20 rad/s)
- **PPO hyperparams** → `agents/rsl_rl_ppo_cfg.py`
- **Override the USD path** → `export DOGGO_USD_PATH=/path/to/your.usd`
- **Override IsaacLab path** → `export ISAACLAB_PATH=/path/to/IsaacLab`

## Where else to find me

- Issues / questions → talk to Claude with the `CLAUDE_HANDOFF.md` file open
- Spot reference (what we modeled this on) →
  `~/IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spot/`

## License
BSD-3-Clause (mirrors Isaac Lab's licensing for the Spot config it adapts).
