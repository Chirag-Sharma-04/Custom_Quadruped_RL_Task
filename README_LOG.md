# Doggo Isaac Lab Detailed Work Log

Purpose: this file is the chronological project log. Update it whenever work is done, training output is received, a decision is made, or an important observation is discovered. It should be detailed enough for a future VM/LLM/user to reconstruct what happened without re-reading the entire conversation.

Timestamp format: `YYYY-MM-DD HH:MM:SS TZ offset`.

## 2026-05-04 12:22:37 IST +0530

### User Direction

The user asked to restart the working process properly "from scratch" and create three README-style files:

1. A detailed log file that records what happened, what was done, what the user provided, and enough context for future continuation.
2. A smaller, human-friendly summary file with TLDR/conclusions.
3. A rules file for future LLMs working on this project.

The user also said they will provide training output at multiple times, and those outputs should be saved for future reference.

### Files Created For Ongoing Process

- `README_LOG.md`: detailed chronological log.
- `README_TLDR.md`: short human-readable project summary.
- `README_LLM_RULES.md`: rules and operating instructions for future LLM sessions.

### Current Repository Context

Repository path:

- `/home/hp/IsaacLab/doggo_isaac_lab_task`

Important source files:

- `doggo_tasks/__init__.py`: registers the training and play Gym environments.
- `doggo_tasks/doggo_cfg.py`: defines Doggo robot USD path, spawn state, joint defaults, and actuator config.
- `doggo_tasks/flat_env_cfg.py`: defines terrain, actions, commands, observations, rewards, events, terminations, and train/play environment configs.
- `doggo_tasks/mdp/rewards.py`: defines custom lateral foot-distance penalty.
- `doggo_tasks/agents/rsl_rl_ppo_cfg.py`: RSL-RL PPO runner config.
- `doggo_tasks/agents/skrl_flat_ppo_cfg.yaml`: skrl PPO config.
- `scripts/train.py`, `scripts/play.py`, `scripts/drop_test.py`: wrappers around Isaac Lab scripts.
- `doggo_tasks/assets/doggo_v2.usd`: bundled Doggo USD asset.

Current git state before adding these README files was clean.

### Key Understanding From Prior Inspection

This is a standalone Isaac Lab task package named `doggo_tasks`. It registers:

- `Isaac-Velocity-Flat-Doggo-v0`
- `Isaac-Velocity-Flat-Doggo-Play-v0`

The task is based on Isaac Lab's Spot flat locomotion task, with Doggo-specific robot config, USD asset, actuator settings, spawn pose, and reward changes.

The current training objective is not just "maximize original Spot reward." The code has been modified to address a specific learned failure mode where the robot could get high scalar reward while visually criss-crossing legs/feet.

### Robot/Asset Understanding

- The robot USD path is resolved from `DOGGO_USD_PATH` if set, otherwise from the bundled `doggo_tasks/assets/doggo_v2.usd`.
- The USD is a binary USD crate, version 0.8.0.
- The USD appears self-contained and exposes expected Doggo prim names and physics schema strings.
- Self-collisions are disabled in the robot config.
- The initial root position is `(0, 0, 0.65)`.
- Joint defaults use asymmetric hip roll and bent hip/knee angles.
- Actuation uses `DelayedPDActuatorCfg`, not `RemotizedPDActuator`.
- Actuator settings include effort limit 100, velocity limit 20, stiffness 60, damping 1.5, and delay range 0-4 physics steps.

### Environment Understanding

- Physics timestep: 0.002 seconds, 500 Hz.
- Control decimation: 10, so policy/control runs at 50 Hz.
- Episode length: 20 seconds.
- Terrain: generated cobblestone/rough style terrain.
- Commands:
  - linear x velocity range: -2 to 3
  - linear y velocity range: -1.5 to 1.5
  - yaw velocity range: -2 to 2
- Observation group is 48-dimensional and includes base velocity, angular velocity, projected gravity, commands, joint position/velocity, and last action.
- Observation corruption/noise is currently disabled even though noise terms are defined.

### Reward Understanding

The current reward setup includes the standard locomotion shaping plus Doggo-specific anti-crossing terms:

- `feet_lateral_distance`: direct geometric penalty for feet too close to/crossing the body centerline.
- `joint_pos_hx`: hip roll posture penalty intended to discourage criss-cross local minima.
- `joint_pos_kn`: knee posture penalty intended to discourage compensation through odd knee postures.

The custom reward in `doggo_tasks/mdp/rewards.py` transforms foot positions into body frame using `quat_apply_inverse`, subtracts `body_y_offset`, and penalizes feet whose absolute lateral distance is below a threshold.

### Previous Training Understanding

Existing extracted training folders are under:

- `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat`

Zip files were intentionally ignored during inspection.

Important extracted runs:

- `2026-04-26_16-21-19`: old reward set, no anti-crossing terms. Best scalar results: reward near 282 last / 296 peak, long episodes near 900 steps, lower final body contact. Likely had the visual criss-cross issue.
- `2026-04-27_10-51-02`: resumed old run with `joint_pos_hx` added. Recovered to around 216 reward.
- `2026-04-27_15-02-24`: full current reward set from scratch, very short/early run.
- `2026-04-27_15-41-32`: full current reward set from scratch, reached around 44 reward.
- `2026-04-27_18-37-39`: full current reward set, longer run, reached around 80 last / 87 peak.
- `2026-04-29_10-26-29`: resumed from `2026-04-27_18-37-39/model_8100.pt`, reached around 65 last / 110 peak.

Conclusion from the training history: the old reward set trained much better numerically but likely learned an unacceptable gait. The current anti-crossing reward set is more physically targeted but appears harder to optimize and has higher body-contact termination rates.

### Known Documentation/Process Issues

- `README.md` still references `CLAUDE_HANDOFF.md`, but that file is deleted in current HEAD.
- `logs/latest.path` points to an older path outside the current repo location.
- `scripts/drop_test.py` can fall back to `random_agent.py` if `zero_agent.py` is missing, so the "no policy" drop test may not always be passive.
- Local Python environment can be sensitive to ROS `PYTHONPATH`; Isaac Sim Python worked when run with `PYTHONPATH` unset.

### Current Working Conclusion

The project is at the stage of balancing gait correctness and trainability. The likely next technical work is to use visual playback plus metrics to compare checkpoints, then adjust reward weights/curriculum only after confirming what the robot is actually doing visually.

Candidate checkpoints for comparison:

- Old high-reward baseline: `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat/2026-04-26_16-21-19/model_10850.pt`
- New anti-crossing run: `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat/2026-04-27_18-37-39/model_8100.pt`
- New resumed run: `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat/2026-04-29_10-26-29/model_10650.pt`

### Training Output Intake Template

When the user provides training output, append a new entry with:

- Exact date/time received.
- Training command or run folder, if known.
- Iteration/checkpoint range.
- Important metrics: mean reward, episode length, body contact, terrain out of bounds, velocity rewards, gait reward, custom penalty terms.
- Any warnings/errors/crashes.
- Short interpretation and next action.

## 2026-05-04 12:30:04 IST +0530

### User Direction

The user asked for an explanation of everything going on in the task.

### Work Done

No code was changed. The explanation focused on the full task flow:

- Gym environment registration.
- Robot/USD configuration.
- Isaac Lab environment configuration.
- What the policy observes and controls.
- Command sampling.
- Reward structure, especially the anti-crossing changes.
- Resets, randomization, and terminations.
- Training/play wrappers.
- Current training-state interpretation.

### Current Interpretation

The task is best understood as a Doggo-specific Isaac Lab velocity-tracking locomotion environment derived from Spot Flat. The current project challenge is no longer just making reward go up; it is finding a reward/termination balance that produces a physically acceptable gait without the criss-cross failure mode while still remaining trainable.

## 2026-05-04 12:52:54 IST +0530

### User Direction

The user clarified the full project plan and deployment target.

### Full Project Plan

The user is training this robot in Isaac Lab using Spot Flat policy/task design as the reference. The goal is to make the modeled Doggo robot as close as practical to the Spot locomotion setup so that the existing Isaac Lab locomotion patterns can be reused.

The policy is not intended for a real physical robot. It will be used only with virtual robots and virtual components inside Isaac Sim. All actuators will be Isaac Sim joints. Real-world actuator dynamics, hardware latency, motor drivers, battery limits, real sensors, and sim-to-real transfer are not the primary target unless explicitly requested later.

Target deployment is future Isaac Sim use, possibly Isaac Sim 4.5, 5.1, or 6.0 depending on what is chosen later. The desired final architecture is:

- Spawn the Doggo robot in any Isaac Sim scene.
- Use an Action Graph or equivalent Isaac Sim/ROS 2 bridge setup.
- Subscribe to joint commands from outside Isaac Sim.
- Publish joint states from Isaac Sim.
- Optionally publish odometry and/or IMU data if needed by the policy node.
- Run the trained locomotion policy as a ROS 2 node.
- Have the ROS 2 policy node communicate with the virtual Doggo in Isaac Sim and make it walk.
- Eventually be able to run the policy ROS 2 node on a Jetson Orin Nano Super.

### Updated Technical Interpretation

The success criterion is a stable, good-looking simulated gait: walking properly, not falling, not criss-crossing, and behaving reliably in Isaac Sim scenes. The priority is not real-robot transfer. This means it is acceptable to make choices that are best for Isaac Sim deployment even if they would be insufficient for physical hardware.

Future work should keep a clean separation between:

- Training environment interface: Isaac Lab observations/actions/rewards.
- Deployment interface: ROS 2 node receiving virtual state and publishing joint commands.
- Isaac Sim scene interface: Action Graph/ROS 2 bridge connecting the virtual robot to the policy node.

### Suggestions Logged

- Treat this as a sim-first locomotion product, not a sim-to-real robotics project.
- Keep the training action/observation interface close to the future ROS 2 deployment interface.
- Decide early what runtime observation inputs the policy node will require: joint states, base angular velocity, gravity orientation, command velocity, previous action, and optionally odometry/IMU.
- Prefer exporting/deploying the trained policy through a format that can run efficiently in ROS 2 on Jetson, likely TorchScript or ONNX after confirming the exact runtime stack.
- Use visual playback as a first-class metric, because high scalar reward previously may have hidden bad gait behavior.

## 2026-05-04 16:57:25 IST +0530

### User Direction

The user answered the deployment questions:

1. Isaac Sim will have a node/interface publishing current joint states and receiving joint commands. The user asked whether the policy can directly give joint states and publish them.
2. Isaac Sim can provide both IMU and odometry data.
3. Flat ground is compulsory. Rough ground is desirable if it is not too much hassle.
4. The desired gait is Spot-like trot.

The user also clarified the previous training results:

- First trained policy was good overall but had criss-cross legs.
- Second trained policy had many problems, including rough-terrain struggle and body-contact issues.

The user asked whether actuator/domain randomization should be removed because the final deployment is only Isaac Sim, where motors and joint dynamics should remain consistent.

### Technical Notes

Current training action is `JointPositionActionCfg` with `scale=0.2` and `use_default_offset=True`. Therefore the policy output should be treated as desired joint position commands, not as measured joint states. Deployment should preserve the distinction:

- Isaac Sim publishes measured/current joint states.
- ROS 2 policy node consumes joint states plus IMU/odom-derived observations.
- ROS 2 policy node publishes desired joint position commands.

The deployed command conversion should reproduce the Isaac Lab action transform:

- `desired_joint_position = default_joint_position + 0.2 * policy_action`

assuming the same joint ordering and default joint positions as training.

Current policy observations include base linear velocity, base angular velocity, projected gravity, command velocity, relative joint position, relative joint velocity, and last action. For deployment:

- joint positions/velocities come from Isaac Sim joint states;
- base angular velocity and gravity orientation can come from IMU;
- base linear velocity can come from odometry;
- previous action must be stored inside the policy node;
- command velocity can come from a user command topic or teleop source.

### Recommendation Logged

For the next training direction, the better strategy is likely not to continue the second policy blindly. The first policy showed that the robot can learn useful locomotion, while the second showed that the anti-crossing penalties made optimization much harder. The preferred next step is a staged retrain:

1. Train/evaluate on flat ground first with Spot-like trot and anti-crossing constraints.
2. Use less aggressive randomization initially.
3. Once flat gait is stable and visually correct, add rough terrain gradually.
4. Keep anti-crossing geometry penalty, but consider softening posture penalties if they are causing body contact or rough-terrain failure.

For sim-only deployment, heavy domain randomization is not required in the same way as sim-to-real. However, small randomization is still useful because Isaac Lab training and Isaac Sim deployment may differ in scene setup, friction, solver behavior, timestep, ROS 2 bridge latency, and terrain/contact details. The recommendation is to narrow randomization, not remove all of it.

Specific randomization guidance:

- Keep some friction variation, but make it modest.
- Reduce or temporarily disable added base mass during early gait learning.
- Reduce push disturbances until the flat trot is stable.
- Keep small actuator/command delay tolerance if ROS 2 bridge latency is expected.
- Avoid broad rough terrain until flat walking is solved.

## 2026-05-04 17:06:41 IST +0530

### User Direction

The user asked whether the constraints from the second edit/run are really needed. The user's reasoning: the first policy was good and better overall except for criss-cross legs, so maybe the better path is to start from the first setup and add only enough reward logic to prevent criss-cross. The second edited run had rough-terrain struggle, body-contact issues, and other problems.

### Recommendation

The recommended direction is to use the first successful setup as the base and add a minimal, targeted anti-crossing fix, rather than keeping all constraints from the second edit at full strength.

Interpretation:

- The first setup proved the robot, actuator config, action space, PPO settings, and base reward structure can learn locomotion.
- The second setup likely added too much posture pressure too early, especially with `joint_pos_hx` and `joint_pos_kn`, while the robot was also dealing with rough terrain/randomization.
- The direct geometric `feet_lateral_distance` reward is the most conceptually correct anti-crossing fix because it penalizes the actual bad outcome.
- The posture penalties should be softened, delayed, or temporarily removed during the next flat-ground retrain unless visual playback proves they are necessary.

Preferred next experiment:

1. Start from the old successful reward structure.
2. Train on flat ground first.
3. Add only the direct foot lateral-distance anti-crossing reward at a moderate weight.
4. Keep gait/trot reward active.
5. Reduce rough terrain and heavy randomization initially.
6. If criss-cross remains, add a small hip-roll posture penalty later.
7. Add knee posture penalty only if the robot uses knee compensation to bypass the foot-spacing reward.

Current best hypothesis: the second run failed not because anti-crossing is a bad idea, but because too many anti-crossing/posture/terrain difficulties were combined too early.

## 2026-05-04 17:11:29 IST +0530

### User Direction

The user asked how sure we are that the proposed updates will work and whether the robot will walk properly.

### Confidence Assessment

The recommendation is a strong engineering hypothesis, not a guarantee. RL locomotion is stochastic and depends on reward balance, robot morphology, solver/contact details, and training duration.

Confidence levels:

- High confidence that the first setup is a better base than the second full-constraint setup, because the first run already produced strong locomotion metrics.
- Medium-high confidence that a direct foot lateral-distance penalty is the right first anti-crossing fix, because it targets the actual observed failure mode.
- Medium confidence that the next staged retrain will produce a better flat-ground gait than the second run.
- Low-to-medium confidence that the first attempt will be perfect without follow-up tuning.

Expected outcome if the hypothesis is right:

- The robot should recover much of the first run's walking ability.
- Criss-crossing should reduce if the lateral-distance reward is weighted correctly.
- Body-contact issues should be lower than in the second run because posture constraints and terrain difficulty are reduced.

Known risk:

- If the lateral-distance penalty is too weak, criss-crossing may remain.
- If it is too strong, the robot may learn wide/awkward foot placement.
- If default joint pose or body/foot geometry assumptions are slightly off, the reward may need tuning.
- Rough terrain should not be judged until flat-ground gait is stable.

## 2026-05-04 17:19:43 IST +0530

### Code Change

Updated `doggo_tasks/flat_env_cfg.py` for the next staged retrain.

Important changes:

- Replaced rough/cobblestone terrain with a true plane terrain for flat-first training.
- Kept the direct `feet_lateral_distance` anti-crossing reward but reduced its weight from `-50.0` to `-25.0`.
- Removed the separate full-strength `joint_pos_hx` and `joint_pos_kn` posture penalties for now.
- Restored old-style general `joint_pos` penalty over all joints with weight `-0.7`.
- Narrowed friction randomization from broad low-friction ranges to `static=(0.8, 1.2)` and `dynamic=(0.7, 1.1)`.
- Reduced base mass randomization from `(-2.5, 2.5)` kg to `(-0.5, 0.5)` kg.
- Reduced push disturbance from `+-0.5 m/s` every 10-15 seconds to `+-0.1 m/s` every 15-20 seconds.
- Set the viewer camera to follow env 0's robot root using `origin_type="asset_root"`.
- Disabled terrain and command debug visualization markers for cleaner/faster video renders.
- Disabled terrain-level curriculum for this plane-terrain stage.

Reasoning:

The next experiment should recover the first run's trainability while adding only a direct, moderate anti-crossing correction. Rough terrain and stronger robustness pressure should be added after flat-ground Spot-like trot is visually clean. Plane terrain is preferred over a 1x1 generated terrain because generated terrain origins can make many envs share the same terrain origin; plane terrain uses grid env origins.

Next run guidance:

- Start a fresh training run for this stage-1 config.
- Do not resume from the second full-constraint run for the first test of this config, because the reward/terrain/randomization setup changed substantially.

Validation:

- `flat_env_cfg.py` passed Python AST syntax parsing.
- A lightweight Isaac Lab import check could not complete in the current shell because `/home/hp/IsaacLab/_isaac_sim/python.sh` reported `ModuleNotFoundError: No module named 'gymnasium'`. This looks like an environment/package issue, not a syntax error.

Camera note:

- Camera following only affects viewport/video rendering. It should not affect headless training without rendering. With `--video`, rendering is already the expensive part; the follow callback should add negligible overhead compared with rendering frames.

## 2026-05-04 17:50:33 IST +0530

### Smoke Test

Ran a tiny headless Isaac Lab training smoke test:

- Command shape: `./isaaclab.sh -p .../scripts/train.py --task Isaac-Velocity-Flat-Doggo-v0 --headless --num_envs 16 --max_iterations 1`
- Result: passed.
- Log folder: `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat/2026-05-04_17-50-14`

Confirmed by Isaac Lab output:

- Environment device: `cuda:0`.
- Physics dt: `0.002`.
- Env step: `0.02`.
- Number of envs in smoke test: `16`.
- Action shape: `12`.
- Observation shape: `48`.
- Reward manager has `15` active terms.
- `feet_lateral_distance` is active at weight `-25.0`.
- `joint_pos_hx` and `joint_pos_kn` are not active.
- Curriculum manager has `0` active terms.
- Push interval is `(15.0, 20.0)`.
- Training completed iteration `0/1`.

Initial smoke metrics are not meaningful for policy quality because this was only one iteration, but they show the environment builds and steps correctly.

### Command Update

Updated `train_cmd.txt` to the intended fresh stage-1 command. Removed the old `--resume --load_run 2026-04-27_18-37-39 --checkpoint model_8100.pt` arguments so the next full run does not accidentally resume from the second full-constraint checkpoint.

## 2026-05-04 17:53:38 IST +0530

### Command Update

The user requested training videos every 500 iterations, with each video lasting 5 seconds.

Updated `train_cmd.txt`:

- `--video_length 250`: 5 seconds because the env step is `0.02s`.
- `--video_interval 12000`: 500 RSL-RL iterations because `num_steps_per_env=24`, so `500 * 24 = 12000` env steps.

## 2026-05-04 17:55:44 IST +0530

### Command Update

The user decided to reduce video overhead. Updated `train_cmd.txt` from 5-second videos to 3-second videos every 500 iterations:

- `--video_length 150`: 3 seconds because the env step is `0.02s`.
- `--video_interval 12000`: still every 500 RSL-RL iterations.

## 2026-05-05 09:58:41 IST +0530

### Training Result

The user provided final output from the fresh stage-1 flat-ground run.

Run folder:

- `/home/hp/IsaacLab/logs/rsl_rl/doggo_flat/2026-05-04_18-25-16`

Run setup confirmed from saved params:

- `num_envs=4096`
- `max_iterations=10000`
- `num_steps_per_env=24`
- `terrain_type=plane`
- `feet_lateral_distance` weight `-25.0`
- `terrain_levels: null`
- final checkpoint: `model_9999.pt`
- videos recorded every 500 iterations: step `0`, `12000`, ..., `240000`

Final user-provided metrics:

- iteration `9999/10000`
- mean reward `366.27`
- mean episode length `961.23`
- mean action std `0.22`
- gait reward `8.8829`
- base linear velocity reward `5.1393`
- feet lateral distance penalty `-0.0616`
- body contact termination `0.0542`
- timeout termination `0.9460`
- terrain out of bounds `0.0000`
- training time `29097.88s` (`08:03:35`)

TensorBoard scalar check:

- peak mean reward: `382.9186` at iteration `9369`
- final mean reward: `366.2704` at iteration `9999`
- final mean episode length: `961.23`
- best/lowest body contact observed: `0.0396` at iteration `8821`
- final body contact: `0.0542`
- peak gait reward: `9.3867` at iteration `9183`
- final gait reward: `8.8829`

Interpretation:

This is numerically the best run so far. It exceeds the old high-reward run and has much lower body-contact termination than the second full-constraint anti-crossing run. The stage-1 changes worked for flat-ground learning. However, this only proves flat-ground performance; it does not prove rough-terrain behavior or final Isaac Sim ROS 2 deployment behavior. The next required check is visual playback/video review for gait quality and criss-cross absence.

## 2026-05-05 12:51:02 IST +0530

### Playback FPS Note

The user reported only about 10 FPS in play mode with either 1 robot or 50 robots on an RTX Pro 4000 Blackwell.

Interpretation:

- Since 1 and 50 robots give similar FPS, the bottleneck is likely viewport/rendering/system state, not robot physics or policy inference.
- The completed headless training run achieved high simulation throughput, so the RL task itself is not fundamentally slow.
- The local machine currently reports CPU governor `powersave`; Isaac Sim also warned about CPU performance profile during earlier runs.
- Recommended checks: run play without `--video`/`--enable_cameras`, try `--rendering_mode performance`, ensure Isaac Sim is using the NVIDIA GPU, monitor GPU utilization while playing, and switch CPU power profile/governor to performance if possible.

## 2026-05-05 12:58:08 IST +0530

### Playback Performance Check

Checked the live play process outside the sandbox.

Observed:

- Command running: `scripts/play.py --task Isaac-Velocity-Flat-Doggo-Play-v0 --num_envs 1 --checkpoint .../model_9999.pt --rendering_mode performance`
- GPU: RTX Pro 4000 Blackwell Generation Laptop GPU
- GPU utilization: about `51%`
- GPU process: Isaac Lab/Isaac Sim Python using about `45%` SM in `nvidia-smi pmon`
- GPU memory used: about `7.1GB / 16.3GB`
- GPU pstate: `P1`
- Isaac Sim Python CPU usage: about `139%`, so roughly 1.4 CPU cores
- CPU governor: `powersave`

Interpretation:

The 10 FPS playback issue is probably not raw GPU saturation and not policy inference. It looks like frame pacing, viewport/render-thread bottleneck, CPU power policy, display/compositor overhead, or Isaac Sim GUI overhead. Low global CPU usage can still hide a single-thread/render-thread bottleneck.

## 2026-05-05 17:36:11 IST +0530

### Startup/Drop Recovery Training Decision

The user asked whether the policy can be fine-tuned or retrained to handle a deployment startup where the robot is first spawned above the ground, falls down, and only then the policy starts.

Interpretation:

- This is possible, but it is a different objective from the clean flat-ground trot that was just trained.
- The current stage-1 policy was trained with the controller active immediately from reset, and body/contact events are still treated as failure/termination conditions.
- Therefore, it should not be assumed that the current policy can recover from an arbitrary passive drop or fallen/body-contact state.
- For practical Isaac Sim deployment, the safer first approach is to avoid the passive uncontrolled fall: spawn at the training pose, hold default joint targets briefly, start the policy with zero command, then ramp the walking command.
- If recovery behavior is required later, train it as a separate robustness/startup stage or separate recovery policy using the current good checkpoint as the baseline. Do not overwrite the strong flat-walking baseline blindly.

Recommended direction:

1. Preserve/export the current best flat-walking checkpoint.
2. For normal scenes, use deployment startup logic: spawn, apply/hold default joint pose, let the robot settle, start policy, ramp commands.
3. Only if passive-drop startup is mandatory, create a new fine-tune experiment that randomizes initial height/orientation/joint pose/velocities or uses dropped-state resets. For true fallen recovery, also adjust body-contact termination and add stand-up/recovery rewards, ideally in a separate stage from locomotion.

## 2026-05-05 18:32:41 IST +0530

### Isaac Sim Startup Clarification

Clarified deployment startup language:

- "Policy/hold commands are ready" means Isaac Sim should receive valid joint position targets at the moment physics starts.
- Setting the robot's joint positions once before pressing Play is not enough if the joint drives/ROS bridge then command zeros or no command.
- The safest startup is to publish/hold the training default joint targets while the simulation starts, use zero velocity command, then switch/ramp into normal policy walking after the robot has valid joint state/IMU/odom feedback.
- If the policy node cannot compute an action until Isaac Sim publishes the first observations, either the policy node should publish default joint targets during startup, or a small hold-pose node/action graph should do it until the policy takes over.

## 2026-05-05 19:04:37 IST +0530

### Training Plan Decision

Current recommendation: do not start another training run immediately. The fresh flat-ground checkpoint `2026-05-04_18-25-16/model_9999.pt` is numerically strong enough that the next step should be visual/playback validation and deployment-interface testing.

Train again only if a specific failure is observed:

- criss-cross gait remains visible,
- robot falls or body-contacts during normal flat walking,
- command tracking is poor in important directions,
- Isaac Sim startup from held default pose is unreliable,
- rough terrain or passive-drop recovery becomes mandatory.

The previous run was trained with full planar velocity commands, not only forward walking:

- `lin_vel_x=(-2.0, 3.0)`
- `lin_vel_y=(-1.5, 1.5)`
- `ang_vel_z=(-2.0, 2.0)`

Therefore the policy should have learned forward/backward, lateral, turning, and combined velocity tracking on flat ground, though actual quality still needs visual validation.
