# Running Integration Tests Locally

## Prerequisites

| Requirement          | Version / Notes                                        |
| -------------------- | ------------------------------------------------------ |
| **Python**           | 3.12 (`>=3.9.18,<3.13`)                                |
| **Poetry**           | 2.x, installed under Python 3.12                       |
| **Docker & Compose** | Latest stable                                          |

---

## Setup

### 1. Start the OMERO server

```bash
docker compose up -d
```

Wait a couple of minutes for the server to fully initialise (Ice on port `6064`, web on port `5080`).

### 2. Install dependencies

```bash
poetry env use python3.12
poetry install --with test,dev
```

### 3. Configure OMERO Web

```bash
poetry run ./configuration_omero.sh
```

### 4. Create the Ice configuration

Create `omerodir/etc/ice.config`:

```properties
omero.host=localhost
omero.port=6064
omero.rootpass=omero
omero.user=root
omero.pass=omero
```

### 5. Generate test data

```bash
cd test/omero-server
poetry run python structure_generator.py
cd ../..
```

---

## Running Tests

### VS Code

1. Install the **Python** extension.
2. Select the Poetry virtualenv as interpreter:
   `Cmd+Shift+P` > **Python: Select Interpreter** > `omero-metrics-...-py3.12`
3. Create `.vscode/settings.json`:

```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["test/integration"],
    "python.envFile": "${workspaceFolder}/.env"
}
```

4. Create `.env` in the project root (use absolute paths):

```env
OMERODIR=/absolute/path/to/omero-metrics/omerodir
ICE_CONFIG=/absolute/path/to/omero-metrics/omerodir/etc/ice.config
DJANGO_SETTINGS_MODULE=omeroweb.settings
```

5. Open the Testing sidebar and run.

### PyCharm

1. Set the interpreter to the Poetry virtualenv:
   **Settings** > **Project** > **Python Interpreter** > `omero-metrics-...-py3.12`
2. Create a **pytest** run configuration (**Run** > **Edit Configurations...** > **+** > **pytest**):

| Field                     | Value                                    |
| ------------------------- | ---------------------------------------- |
| **Target**                | `test/integration/test_index.py`         |
| **Working directory**     | Project root                             |
| **Environment variables** | See below                                |

```
OMERODIR=/absolute/path/to/omero-metrics/omerodir
ICE_CONFIG=/absolute/path/to/omero-metrics/omerodir/etc/ice.config
DJANGO_SETTINGS_MODULE=omeroweb.settings
```

3. Click **Run** or **Debug**.

---

## Troubleshooting

| Error | Cause | Fix |
| ----- | ----- | --- |
| `OMERODIR not set` | Missing environment variable | Export `OMERODIR` pointing to `omerodir/` |
| `Permission denied: '/opt/omero'` | `OMERODIR` set to a system path | Use the local `omerodir/` directory instead |
| `Ice.FileException: ice.config` | File does not exist | Create it manually (see step 4) |
| `"omero.host" not set` | `ICE_CONFIG` not exported | `export` the variable; inline env vars don't propagate through `poetry run` |

