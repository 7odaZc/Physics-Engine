# Simple Physics Engine for Gaming

A complete Pygame project for the **SWGCG 352 Project**: a modular physics engine plus an interactive game that demonstrates multiple physics modules.

## Implemented modules

- Particle system with gravity, lifespan, and burst emission
- Mass-spring soft body using verlet integration
- Position-Based Dynamics rope/chain solver
- Rigid body circles with linear motion, angular motion, and collisions
- Forward kinematics and inverse kinematics for a 2-link arm
- **Ball Smash**, a small arcade game built from the rigid-body system
- Interactive demo scenes with a menu and controls

## How to run

```bash
pip install -r requirements.txt
python main.py
```

## Controls

- `1` Ball Smash game
- `2` Particle system demo
- `3` Mass-spring soft body demo
- `4` PBD rope demo
- `5` Rigid body demo
- `6` Kinematics demo
- `R` Reset current scene
- `ESC` Quit

### Ball Smash controls

- Left click or press `Space` to shoot a ball toward the mouse
- Pop the falling targets before they hit the ground
- Your score increases when you hit or break targets
- The game lasts 60 seconds

### Scene controls

**Particle demo**
- Move the mouse to move the emitter
- Left click to burst particles

**Mass-spring demo**
- Left click and drag a node
- Press `R` to reset the soft body

**PBD rope demo**
- Left click and drag the rope end
- Press `R` to reset the rope

**Rigid body demo**
- Left click to spawn a ball
- Right click to spawn a bigger ball
- Hold `SPACE` to create a downward impulse burst
- Press `R` to reset the world

**Kinematics demo**
- Move the mouse to set the IK target
- Press `E` to toggle elbow mode
- Press `R` to reset the arm

## Notes

This project is designed so that all physics systems are visible in one application and can be tested independently. It is fully asset-free, so it runs without external images or audio.
