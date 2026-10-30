# testbed_navigation

Manual Nav2 bringup for the Testbed-T1.0.0 robot (ROS 2 Humble, Gazebo Classic).
Instead of calling `nav2_bringup`, each stage (map, localization, navigation) is
launched separately with its own Nav2 nodes and parameter file.

## Contents

| File | Purpose |
|---|---|
| `launch/map_loader.launch.py` | `map_server` + lifecycle manager, loads `testbed_bringup/maps/testbed_world.yaml` |
| `launch/localization.launch.py` | `amcl` + lifecycle manager |
| `launch/navigation.launch.py` | `controller_server`, `planner_server`, `behavior_server`, `bt_navigator` + lifecycle manager |
| `config/amcl_params.yaml` | AMCL parameters |
| `config/nav2_params.yaml` | Planner, controller, costmaps, behaviors, BT navigator |
| `rviz/nav.rviz` | RViz layout (Fixed Frame `map`, costmaps, plans, particles) |

## How to run

Requires `ros-humble-navigation2`. Build and source the workspace, then use four terminals:

```bash
# 1. Simulation (Gazebo + RViz)
ros2 launch testbed_bringup testbed_full_bringup.launch.py
# 2. Map
ros2 launch testbed_navigation map_loader.launch.py
# 3. Localization
ros2 launch testbed_navigation localization.launch.py
# 4. Navigation (wait for AMCL to report "Managed nodes are active")
ros2 launch testbed_navigation navigation.launch.py
```

Optional navigation RViz layout:

```bash
ros2 run rviz2 rviz2 -d $(ros2 pkg prefix testbed_navigation)/share/testbed_navigation/rviz/nav.rviz --ros-args -p use_sim_time:=true
```

Set goals with **2D Goal Pose** while the RViz Fixed Frame is `map`.

## Design

- **Map:** `nav2_map_server`, brought up by `nav2_lifecycle_manager` (autostart).
- **Localization:** AMCL with the differential motion model and likelihood-field
  laser model. The initial pose matches the robot's Gazebo spawn (0, 5), so the
  filter starts localized. Frames: `map`, `odom`, `base_footprint`; scan on `/scan`.
- **Global planner:** NavFn (Dijkstra) over a global costmap
  (static, obstacle and inflation layers).
- **Local controller:** DWB with a rolling-window local costmap.
- **Behavior tree:** the default Nav2 navigate-to-pose tree, with spin, backup
  and wait recoveries from `behavior_server`.
- Only basic functionality is configured; `velocity_smoother` and
  `collision_monitor` were left out.

The footprint is modeled as a circle (`robot_radius: 0.2`), an estimate from the URDF.

## Bugs found in the starter code

See `BUGS.txt` in the repository root. Four issues were fixed: a malformed
`ament_package()`, a wrong map image path, a missing `maps` install rule, and
a lidar range too short for localization.

## Challenges

- **Frame of goals:** Goals sent while RViz's Fixed Frame was `odom` worked for a
  few seconds, then failed with "extrapolation into the past" TF errors, because
  the goal timestamp aged out of the TF buffer during re-planning. Using Fixed
  Frame `map` for goals and initial poses fixed it.
- **Lifecycle startup:** Nodes only become active when a lifecycle manager
  configures them, and AMCL needs the map first, so the launch order matters.
- **Install rules:** the map was invisible to `map_server` until the `maps`
  directory was installed.

## Results

TODO: add screenshots in `docs/` and/or a video link.

Author: TODO your name