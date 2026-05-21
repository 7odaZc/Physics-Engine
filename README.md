# Physics Engine / Star Shooter

## Overview
This project is a physics simulation application developed using Python and Pygame.  
The application contains multiple interactive physics demonstrations and a small arcade game called **Star Shooter**.

The purpose of the project is to demonstrate the implementation of different physics systems such as:

- Particle Systems
- Mass-Spring Soft Bodies
- Position-Based Dynamics (PBD)
- Rigid Body Dynamics
- Forward and Inverse Kinematics

---

# Main Features

## 1. Star Shooter Game
A small arcade shooting game built using the rigid-body system.

### Features
- Player movement
- Enemy spawning
- Bullet shooting system
- Collision detection
- Score system
- Lives system
- Win and lose screens
- Particle explosion effects

### Controls
| Key | Action |
|-----|--------|
| A / Left Arrow | Move Left |
| D / Right Arrow | Move Right |
| Space / Left Click | Shoot |
| R / Enter | Restart Game |

---

## 2. Particle System
A particle simulation scene used to create effects such as explosions and trails.

### Features
- Gravity effect
- Velocity-based motion
- Particle fading
- Burst emission

### Controls
| Action | Result |
|--------|--------|
| Move Mouse | Move emitter |
| Left Click | Create particle burst |

---

## 3. Mass-Spring Soft Body
A deformable soft-body simulation based on springs and point masses.

### Features
- Spring constraints
- Verlet integration
- Interactive dragging
- Stable pinned points

### Controls
| Action | Result |
|--------|--------|
| Left Click + Drag | Move soft-body nodes |

---

## 4. PBD Rope Simulation
A rope simulation using Position-Based Dynamics.

### Features
- Rope constraints
- Segment stabilization
- Interactive endpoint dragging

### Controls
| Action | Result |
|--------|--------|
| Left Click + Drag | Move rope end |

---

## 5. Rigid Body Dynamics
A physics simulation for circular rigid bodies.

### Features
- Gravity
- Collision response
- Friction
- Angular velocity
- Bounce simulation

### Controls
| Key / Action | Result |
|--------------|--------|
| Left Click | Spawn small body |
| Right Click | Spawn large body |
| Hold Space | Apply force impulse |

---

## 6. Kinematics System
A robotic arm simulation demonstrating Forward and Inverse Kinematics.

### Features
- Two-link arm system
- Inverse kinematics targeting
- Elbow mode switching

### Controls
| Key / Action | Result |
|--------------|--------|
| Move Mouse | Change target position |
| E | Toggle elbow mode |

---

# Scene Switching

| Key | Scene |
|-----|-------|
| 1 | Star Shooter |
| 2 | Particle System |
| 3 | Mass-Spring Soft Body |
| 4 | PBD Rope |
| 5 | Rigid Body Dynamics |
| 6 | Kinematics |
| R | Reset Current Scene |
| ESC | Exit Application |

---

# Technologies Used

- Python 3
- Pygame

---

# Project Structure

```text
main.py

engine/
│
├── particle.py
├── mass_spring.py
├── pbd.py
├── rigid_body.py
└── kinematics.py

game/
│
├── app.py
└── scenes.py
