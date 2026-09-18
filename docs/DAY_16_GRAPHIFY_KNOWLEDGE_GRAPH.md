# Devotics Robotic Arm V1 — Engineering Build Log (Day 16)

**Packages:** `devotics_arm_description`, `devotics_arm_moveit_config`  
**ROS 2 Distribution:** Jazzy / Ubuntu 24.04 (arm64)  
**Topic:** Agentic Architecture — Codebase Knowledge Graphing with Graphify  
**Target:** Transforming the ROS 2 Robotics Repository into a Queryable Knowledge Graph  

---

## 📌 Goal & Overview
As a robotics project grows from a single URDF into multiple packages (descriptions, launch scripts, controllers, MoveIt configs, xacros, kinematics solvers), traditional file-by-file search (grep / find) slows down AI agents and consumes excessive token context.

On Day 16, we implemented **Graphify** (`graphifyy` on PyPI) to parse the entire ROS 2 workspace into a deterministic, queryable Abstract Syntax Tree (AST) knowledge graph.

---

## 🛠️ Implementation Steps

### 1. Standalone `uv` Tool Installation
On Ubuntu 24.04, standard `pip` is restricted by PEP 668 ("externally-managed-environment"), and system-level packages require sudo passwords. We installed Astral's **`uv`** package manager in user space (`~/.local/bin`):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
```

### 2. Installing Graphify Globally
```bash
uv tool install graphifyy
```
This installs the `graphify` CLI executable into `~/.local/bin/graphify` with all dependencies (`tree-sitter`, `networkx`, `rapidfuzz`).

### 3. Extracting the AST Knowledge Graph
We ran Graphify on both packages using `--code-only` (local AST parsing without requiring an external cloud LLM API key):
```bash
cd ~/ros2_ws/src/devotics_arm_description
~/.local/bin/graphify . --code-only
~/.local/bin/graphify cluster-only ~/ros2_ws/src/devotics_arm_description

cd ~/ros2_ws/src/devotics_arm_moveit_config
~/.local/bin/graphify . --code-only
~/.local/bin/graphify cluster-only ~/ros2_ws/src/devotics_arm_moveit_config
```

### 4. Registering Native Antigravity Skill
We installed the Graphify skill into the workspace customizations root:
`devotics_arm_description/.agents/skills/graphify/SKILL.md`

Antigravity can now natively navigate god nodes, community clusters, and architectural dependencies across the project.

---

## ⚠️ Obstacles, Mistakes & How They Were Solved

### Obstacle 1: The Missing Pip & Sudo Wall
* **The Error:** Attempting `pip install graphifyy` returned:
  `/bin/sh: 1: pip: not found`
  And attempting `sudo apt install python3-pip` failed because passwordless sudo is disabled (`sudo: a password is required`).
* **How We Solved It:** Used `curl -LsSf https://astral.sh/uv/install.sh | sh`. This downloads pre-compiled standalone Rust binaries directly to `~/.local/bin/`, completely bypassing system apt, sudo, and Python virtualenv restrictions.

### Obstacle 2: The "No LLM API Key Found" Error
* **The Error:** Running `graphify .` initially failed with:
  `error: no LLM API key found (8 doc/paper/image file(s) need semantic extraction).`
* **Why it happened:** By default, Graphify attempts to send non-code markdown files to Gemini/Claude for semantic summarization. If `GEMINI_API_KEY` or `GOOGLE_API_KEY` is not exported in the shell environment, it halts.
* **How We Solved It:** Ran with the `--code-only` flag followed by `graphify cluster-only <path>`. This performs 100% local, deterministic AST extraction on Python and C++ files, builds the community graph, and outputs `graph.html` and `GRAPH_REPORT.md` with zero API calls and zero token costs.

---

## 📊 Knowledge Graph Metrics

### In `devotics_arm_description`:
* **Nodes:** 27
* **Edges:** 31
* **Communities:** 6 modular clusters
* **Key Hubs Identified:** `display.launch.py`, `ik_demo.py`, `solve_ik_2d()`

### In `devotics_arm_moveit_config`:
* **Nodes:** 18
* **Edges:** 24
* **Communities:** 8 modular clusters

---

## ✅ How to View the Interactive 3D Graph
To view the interactive visual knowledge graph in your browser:
```bash
xdg-open ~/ros2_ws/src/devotics_arm_description/graphify-out/graph.html
```
Or view the markdown summary:
```bash
cat ~/ros2_ws/src/devotics_arm_description/graphify-out/GRAPH_REPORT.md
```
