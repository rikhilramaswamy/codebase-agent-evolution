# Codebase Onboarding Agent: Hardening an Enterprise-Grade Knowledge Server Across Evolving Runtimes


> **Disclaimer:** This repository is a refactored version of the original project. The Kaggle notebooks remain the ultimate source of truth for the codebase execution, raw metrics, and historical evaluation logging.

> **Systems Optimization Milestone:** By systematically identifying and treating infrastructure constraints as variables, this project engineered out framework and OS-level bottlenecks to compress steady-state query latencies from **83.83s** down to a blistering **3.58s**—achieving a **23x performance leap (-95.7% latency reduction)**.

### 🔗 Core Project Resources
* 📺 **System Walkthrough & Live Demo:** [YouTube Video Walkthrough (Architectural Breakdown)](https://www.youtube.com/watch?v=NIN9FZ1fMfE)
* 🧠 **Definitive Submission Writeup:** [Master Capstone Engineering Writeup on Kaggle](https://www.kaggle.com/competitions/vibecoding-agents-capstone-project/writeups/codebase-agenthardening-an-enterprise-knowledge-s)
* ⚙️ **Production Run Kernels:**
  * [Phase 0: Hierarchical Multi-Agent Graph Baseline](https://www.kaggle.com/code/nikhilramaswamy/codebase-onboarding-agent)
  * [Phase 1: Single-Agent via Ephemeral Skills](https://www.kaggle.com/code/nikhilramaswamy/adk-phase-1-single-agent-skills-refactor/)
  * [Phase 2: Production-Grade Persistent MCP Daemon](https://www.kaggle.com/code/nikhilramaswamy/adk-phase-2-persistent-service-port-refactor/)

---

## 🧠 The Architectural Paradigm: Constant Data vs. Evolving Compute

To establish an ironclad scientific baseline, this architecture strictly decouples the invariant **Data Asset Layer** from the experimental **Compute Engine Topology**. The repository workload remains a universal constant across all execution turns, ensuring that all measured performance leaps are driven entirely by runtime infrastructure hardening.

### 📦 1. The Data Asset (Universal Constant)
The source repository analysis is fully isolated from the agent's online execution layer and packaged into a single immutable artifact (**The Kaggle Code Knowledge Pack**):
* **Structural Topology:** A pre-computed `NetworkX` directed graph in GraphML format, capturing the precise abstract syntax tree and call-graph dependencies.
* **Semantic Index:** A localized `ChromaDB` collection mapping vector representations of code snippet chunks.

### ⚙️ 2. The Compute Engine (Evolving Topologies)
The agent runtime systematically evolved through three development phases to erase specific infrastructure bottlenecks:

* **Phase 0 (Legacy Multi-Agent Graph):** Orchestration spread across separate, specialized worker agents (Supervisor + Specialist Workers). Passing tasks across agent chat boundaries created a heavy **Framework Serialization Tax (83.83s Latency)**.
* **Phase 1 (Modular Agent Skills):** Collapsed the multi-agent graph into a singular agent using custom local skills invoked as subprocesses. This erased conversational routing delays but unmasked an **OS-Level Subprocess Forking Tax (24.02s Latency)** due to cold disk reads and package re-imports on every tool invocation.
* **Phase 2 (Persistent Service Paradigm):** Kept the streamlined single-agent reasoning model but backed it with a long-lived background **Model Context Protocol (MCP)** server daemon. The indexes are pinned to hot RAM exactly once upon boot, turning heavy disk I/O into instantaneous object reference lookups **(3.58s Latency)**.

---

## 📊 Systems Performance Matrix

All phases were benchmarked using identical code exploration queries against the same underlying data pack:

| Evaluation Target / Scenario | Metric Type | Phase 0 <br> *(Hierarchical Graph)* | Phase 1 <br> *(Modular Skills)* | Phase 2 <br> *(Persistent MCP Server)* |
| :--- | :--- | :---: | :---: | :---: |
| **Query 1** <br> *Multi-Turn Pipeline Logic* | Latency <br> Token Volume | `12.69s` <br> 5,612 | `23.35s` <br> 4,744 | `29.51s` <br> **22,426** |
| **Query 2** <br> *Steady-State Structural Sweep* | Latency <br> Token Volume | `83.83s` <br> 7,439 | `24.02s` <br> 12,085 | **`3.58s`** <br> 6,661 |
| **Query 3** <br> *Reverse Dependency Trace* | Latency <br> Token Volume | `11.73s` <br> 9,907 | `22.09s` <br> 14,832 | **`5.98s`** <br> 13,869 |


### 🔍 Critical Production Insights
1. **The Orchestration Tax Eradication (V0 -> V1):** Query 2 demonstrates that distributed agent choreography is an anti-pattern for tightly coupled analytical code tasks. Collapsing the worker topology into focused single-agent skills compressed latency from **83.83s to 24.02s (-71.3%)**.
2. **The Subprocess Fork Tax Destruction (V1 -> V2):** Transitioning from stateless script boundaries to a persistent JSON-RPC protocol tunnel via FastMCP compressed structural sweeps down to **3.58s (-85.1%)**. 
3. **Contextual Volume Expansion (Query 1):** Phase 2 exhibits higher turn-1 latency because it safely ingested **22,426 tokens** (compared to V0's 5,612). Keeping indices hot allows the Google ADK planner to trace deep, multi-layered code variables in a single, un-severed turn without hitting framework memory walls.

---

## 🛡️ Enterprise Safety & Production Hardening

To satisfy real-world deployment constraints, the system implements three core architectural security pillars:
* **Pillar I: Thread-Safe Double-Checked Lazy Initialization Guard:** Resource loading is deferred until the first tool execution to support instant container handshakes. Concurrent turn-1 tool threads are wrapped in a mutual-exclusion `threading.Lock()` using double-checked verification validation to block data races.
* **Pillar II: Clean Dependency Injection:** Zero credentials or local filesystem paths are hardcoded. The orchestration loop relies entirely on strict dependency injection, passing environment vectors dynamically at container execution runtime.
* **Pillar III: Isolated Telemetry Channeling:** In strict compliance with the MCP specification, standard output (`stdout`) is completely reserved for structured JSON-RPC communication frames. All internal system logs, debugging hooks, and exceptions are isolated over standard error channels (`stderr`), preventing stream corruption.

---

## 📁 Repository Structure

```text
├── shared/                  # Universal constant configurations and metric evaluation log loops
├── v0_multi_agent/          # Legacy supervisor-worker orchestration graph (Kaggle Baseline)
├── v1_single_agent_skills/  # Collapsed single-agent topology running isolated subprocess tools
└── v2_mcp_daemon/           # Production implementation utilizing a persistent background FastMCP server
```


## 🛠️ Quickstart Installation & Execution

Each architecture directory contains an isolated, executable agent_driver.py serving as the definitive entry point for that phase.

1. Environment Setup
Clone the repository and install the verified systems dependencies:
    ```text
    git clone [https://github.com/YOUR_USERNAME/codebase-agent-evolution.git](https://github.com/YOUR_USERNAME/codebase-agent-evolution.git)
    cd codebase-agent-evolution
    pip install -r requirements.txt
    ```


2. Prepare Data
Download the necessary Code Knowledge Pack (MCP archive) and update the MCP_ARCHIVE_PATH in shared/config_setup.py to point to its location.

3. Configure Credentials
Export your Google GenAI credential matrix:
    ```text
    export GEMINI_API_KEY="your_api_key_here"
    ```

4. Run the Agent
To run the high-performance Phase 2 Persistent Service daemon, navigate to the target module and trigger the execution driver:
    ```text
    cd v2_mcp_daemon
    python agent_driver.py
    ```


## 🚀 The Future Roadmap
* Phase 3 (IDE Integration): Mounting the persistent native background daemon into active developer interfaces (Cursor / Claude Desktop) over active JSON-RPC sockets.

* Phase 4 (Autonomous CI Evaluation): Instantiating a closed-loop "Golden Dataset" regression-testing suite to benchmark reasoning paths against live code updates.

* Phase 5 (Git Automation Hooks): Triggering asynchronous NetworkX call-graph re-indexing pipelines tied directly to active repository commit webhooks.