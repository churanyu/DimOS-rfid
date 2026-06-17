# DimOS RFID module

DimOS integration for your **Vulcan RFID scanner**, built on top of the existing code in [`rfid scanner python/`](../rfid%20scanner%20python/).

## What’s in this folder

| File | Purpose |
|------|---------|
| `rfid_module.py` | DimOS `Module` — publishes `rfid_tags` stream + agent skills |
| `msgs.py` | `RfidTag` / `RfidTagArray` message types (with Rerun rendering) |
| `_backend.py` | Imports your `rfid_service.py` for direct mode |
| `demo_blueprint.py` | RFID + viewer only (no robot) |
| `go2_blueprints.py` | Go2 spatial / agentic stacks + RFID |
| `__main__.py` | CLI runner (`python -m dimos_rfid`) |

## Prerequisites

1. **DimOS** installed (Linux machine that can talk to the dog):

   ```bash
   uv pip install 'dimos[base,unitree]'
   ```

2. **RFID HTTP server** on the robot (recommended for first test):

   ```bash
   cd "rfid scanner python"
   python3 rfid_scanner_server.py
   ```

3. Install this package into the same venv:

   ```bash
   cd dimos_rfid
   pip install -e .
   # or from repo root:
   pip install -e ./dimos_rfid
   ```

---

## Quick start (no `dimos run` required)

### 1. RFID demo — viewer + tags only

```bash
# DimOS on your laptop polls the robot's HTTP API
export RFID_API_BASE=http://10.42.200.240:8765/api/v1
python -m dimos_rfid demo
```

You should see the Rerun window; RFID status appears as text logs when tags are in range.

### 2. Go2 + RFID (SLAM, map, camera)

```bash
export ROBOT_IP=YOUR_GO2_IP
export RFID_API_BASE=http://10.42.203.26:8765/api/v1
python -m dimos_rfid go2
```

### 3. Go2 + RFID + LLM agent

```bash
export ROBOT_IP=YOUR_GO2_IP
export RFID_API_BASE=http://10.42.203.26:8765/api/v1
python -m dimos_rfid go2-agentic
```

Then in another terminal:

```bash
dimos mcp call get_active_rfid_tags
dimos agent-send "what RFID tags do you see?"
```

---

## Connection modes

| Mode | When to use | Config |
|------|-------------|--------|
| **http** (default) | `rfid_scanner_server.py` running on robot | `RFID_API_BASE=http://host:8765/api/v1` |
| **direct** | DimOS process can reach reader at `192.168.123.2` | `RFID_CONNECTION_MODE=direct` |

Direct mode uses your `rfid_service.RfidScanner` in-process (no Flask server).

---

## How to “add” a module to DimOS

DimOS discovers runnable stacks via **`all_blueprints.py`** inside the `dimos` package. Your code lives **outside** that package, so you have **three options**:

### Option A — Run from this repo (easiest, no DimOS changes)

Use the entry point above:

```bash
python -m dimos_rfid demo
python -m dimos_rfid go2-agentic
```

This calls `ModuleCoordinator.build(blueprint).loop()` — the same runtime as `dimos run`, without registering a CLI name.

### Option B — One-liner from Python

```python
from dimos.core.coordination.module_coordinator import ModuleCoordinator
from dimos_rfid.go2_blueprints import unitree_go2_rfid_agentic

ModuleCoordinator.build(unitree_go2_rfid_agentic).loop()
```

### Option C — Register `dimos run rfid-demo` (inside DimOS source tree)

If you clone [dimensionalOS/dimos](https://github.com/dimensionalOS/dimos), copy or symlink this package:

```bash
cd dimos   # your dimos git clone
ln -s /path/to/Dimos/dimos_rfid dimos/hardware/sensors/rfid
```

Add a thin blueprint file so auto-discovery finds it:

```python
# dimos/hardware/sensors/rfid/demo_blueprint.py
from dimos_rfid.demo_blueprint import rfid_demo  # noqa: F401 — re-export
```

Or copy `demo_blueprint.py` into `dimos/hardware/sensors/rfid/` and fix imports to be relative to `dimos`.

Regenerate the CLI registry:

```bash
pytest dimos/robot/test_all_blueprints_generation.py
```

Then:

```bash
dimos run rfid-demo
dimos list   # should show rfid-demo
```

**Rules for CLI registration:**

- Blueprint variable must be a **top-level** `autoconnect(...)` assignment (not inside a function).
- Name `rfid_demo` becomes CLI name `rfid-demo`.
- File must live under the `dimos/` Python package tree.

### Option D — Compose into an existing blueprint

In your own blueprint file inside the dimos repo:

```python
from dimos.core.coordination.blueprints import autoconnect
from dimos_rfid.rfid_module import RfidModule
from dimos.robot.unitree.go2.blueprints.agentic.unitree_go2_agentic import unitree_go2_agentic

my_go2_with_rfid = autoconnect(
    unitree_go2_agentic,
    RfidModule.blueprint(api_base="http://192.168.123.18:8765/api/v1"),
)
```

---

## Module API

### Stream

- **`rfid_tags`** → `Out[RfidTagArray]` on LCM topic `/rfid/tags`

Subscribe from another module:

```python
class MyListener(Module):
    rfid_tags: In[RfidTagArray]

    @rpc
    def start(self):
        super().start()
        self.rfid_tags.subscribe(self._on_tags)

    def _on_tags(self, msg: RfidTagArray):
        print(msg.active_tags())
```

### Agent skills (on `RfidModule`)

| Skill | Description |
|-------|-------------|
| `get_active_rfid_tags()` | Tags currently in range |
| `lookup_rfid_tag(epc)` | One tag by EPC |
| `get_rfid_reader_status()` | Reader health |

Skills are available when the blueprint includes `McpServer` (e.g. `go2-agentic`).

### Debug LCM topic

```bash
dimos topic echo /rfid/tags
```

---

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RFID_API_BASE` | `http://localhost:8765/api/v1` | HTTP API base URL |
| `RFID_CONNECTION_MODE` | `http` | `http` or `direct` |
| `VULCAN_READER_HOST` | `192.168.123.2` | Reader IP (direct mode) |
| `VULCAN_READER_USER` | `admin` | Digest auth user |
| `VULCAN_READER_PASS` | `admin` | Digest auth password |

---

## Next steps (your localization plan)

1. **`RfidLocalizerModule`** — subscribe to `rfid_tags` + robot `odom`, fuse RSSI + pose
2. **Rerun markers** — extend `RfidTagArray.to_rerun()` with `Points3D` / `Arrows3D` at estimated positions
3. **`SpatialMemory`** — persist “last seen” locations for occluded objects

---

## Layout

```
Dimos/
├── rfid scanner python/     # your existing API (unchanged)
│   ├── rfid_service.py
│   └── rfid_scanner_server.py
└── dimos_rfid/              # this package
    ├── rfid_module.py
    ├── msgs.py
    ├── demo_blueprint.py
    ├── go2_blueprints.py
    └── README.md
```
