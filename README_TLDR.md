# Doggo Isaac Lab TLDR

This is the short human-friendly status file. Keep it updated with conclusions, not every detail.

## Current Status - 2026-05-05 09:58:41 IST +0530

We created a three-file tracking system:

- `README_LOG.md`: detailed chronological project log.
- `README_TLDR.md`: this short summary.
- `README_LLM_RULES.md`: rules for future LLM sessions.

The project is a standalone Isaac Lab Doggo locomotion task based on Spot Flat. It registers `Isaac-Velocity-Flat-Doggo-v0` for training and `Isaac-Velocity-Flat-Doggo-Play-v0` for playback.

Deployment goal: this is sim-only. The trained policy is intended to control a virtual Doggo in Isaac Sim, not a real robot. Future deployment should run the policy as a ROS 2 node that communicates with Isaac Sim joints through Action Graph/ROS 2 bridge style interfaces, with joint states and optionally odometry/IMU coming back from Isaac Sim. The policy node may eventually run on a Jetson Orin Nano Super.

Main understanding:

- The old training run from `2026-04-26_16-21-19` achieved much better scalar reward, but likely had a bad criss-cross gait.
- The newer reward setup adds anti-crossing penalties: lateral foot distance, hip roll posture, and knee posture.
- The newer runs are more physically targeted but train slower and show more body-contact terminations.
- The next useful step is visual playback of old vs new checkpoints before changing reward weights again.
- The training interface should stay close to the future ROS 2 deployment interface so policy export/deployment is not painful later.
- Deployment should treat policy output as desired joint position commands, not measured joint states.
- Current best strategy: solve flat-ground Spot-like trot first with gentler randomization, then gradually add rough terrain.
- Since deployment is sim-only, use narrow robustness randomization rather than broad sim-to-real randomization.
- Recommended next training direction: go back toward the first successful setup, add only a minimal direct anti-crossing reward first, and avoid the full second-run constraint bundle until the flat trot is clean.
- Code now follows that direction: flat plane terrain, moderate direct foot-spacing penalty, old-style all-joint posture penalty restored, hip/knee special posture penalties removed, randomization/pushes narrowed, terrain curriculum disabled, and camera set to follow env 0's robot.
- Next run should be fresh, not resumed from the second full-constraint checkpoint.
- A 16-env, 1-iteration headless smoke test passed. Isaac Lab confirmed 48 obs, 12 actions, 15 reward terms, `feet_lateral_distance=-25.0`, and 0 curriculum terms.
- `train_cmd.txt` now contains the fresh stage-1 command with no resume flags.
- `train_cmd.txt` records 3-second videos every 500 training iterations: `--video_length 150 --video_interval 12000`.
- Fresh stage-1 run `2026-05-04_18-25-16` completed 10k iterations. Final reward was `366.27`, peak reward was `382.92`, final episode length was `961.23`, body contact was about `5.4%`, timeout was about `94.6%`, and terrain out-of-bounds was `0`.
- Current conclusion: the flat-ground stage-1 training worked very well numerically. Next decision should be based on video/playback quality, especially whether criss-cross is gone.
- Playback FPS around 10 with both 1 and 50 robots likely points to viewport/rendering/system power state, not policy/physics. Try performance rendering mode and check CPU/GPU power state.
- Live check during play showed GPU around `51%`, Isaac Sim Python around `139%` CPU, and CPU governor still `powersave`; likely main/render-thread or frame-pacing bottleneck rather than GPU saturation.
- Startup/drop recovery is possible to train, but it should be treated as a separate robustness stage. For deployment, prefer spawning in the training pose, holding default joint targets briefly, starting the policy at zero command, then ramping commands. Do not assume the current walking policy can recover from an uncontrolled passive fall.
- For Isaac Sim startup, "hold commands are ready" means valid default joint position targets are already being published/held when physics starts. Setting joint positions once is not enough if drives/ROS commands then go to zero or disappear.
- No new training is recommended until `model_9999.pt` is visually tested. The previous run already trained velocity commands in x, y, and yaw, so it should handle forward/backward, sideways, turning, and combined flat-ground commands within its trained ranges.

Best checkpoints to compare:

- Old high-reward baseline: `2026-04-26_16-21-19/model_10850.pt`
- New anti-crossing run: `2026-04-27_18-37-39/model_8100.pt`
- New resumed run: `2026-04-29_10-26-29/model_10650.pt`

When new training output is provided, save the useful metrics in `README_LOG.md` and put only the conclusion here.
