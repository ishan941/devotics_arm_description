# Graph Report - devotics_arm_description  (2026-09-18)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 27 nodes · 31 edges · 6 communities (2 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `41fab9bf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- display.launch.py
- ik_demo.py
- subprocess
- diagnose_and_fix.py
- apply_all_fixes.py
- os

## God Nodes (most connected - your core abstractions)
1. `solve_ik_2d()` - 2 edges
2. `Solves Inverse Kinematics for a 2-link planar arm in the (X, Z) plane. Returns…` - 1 edges
3. `Day 12: Inverse Kinematics (IK) Intuition Script for Devotics Arm Demonstrates…` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Import Cycles
- None detected.

## Communities (6 total, 4 thin omitted)

### Community 0 - "display.launch.py"
Cohesion: 0.33
Nodes (4): ament_index_python_packages, launch, launch_ros_actions, xacro

### Community 1 - "ik_demo.py"
Cohesion: 0.40
Nodes (4): math, Solves Inverse Kinematics for a 2-link planar arm in the (X, Z) plane. Returns…, Day 12: Inverse Kinematics (IK) Intuition Script for Devotics Arm Demonstrates…, solve_ik_2d()

## Knowledge Gaps
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Not enough signal to generate questions. This usually means the corpus has no AMBIGUOUS edges, no bridge nodes, no INFERRED relationships, and all communities are tightly cohesive. Add more files or run with --mode deep to extract richer edges._