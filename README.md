# ImmichFrame Editor

A simple, elegant web UI for managing [ImmichFrame](https://immichframe.dev) — the digital photo frame companion to [Immich](https://immich.app).

Instead of editing YAML files directly, this Flask web app lets you:
- ✅ Select which **people** to display (with thumbnails from Immich)
- ✅ Select which **albums** to display
- ✅ Configure timing, clock, and display options
- All changes saved to `Settings.yml` and ImmichFrame restarts automatically

## Requirements

- [Immich](https://immich.app) server running and accessible
- [ImmichFrame](https://immichframe.dev) already configured and working
- Docker

## Quick Start

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/immichframe-editor.git
cd immichframe-editor
```

### 2. Configure your ImmichFrame path

Edit `docker-compose.yml` — update the volume mount to point to your ImmichFrame config directory:

```yaml
volumes:
  - ./app:/app
  - /var/run/docker.sock:/var/run/docker.sock
  - /path/to/your/immichframe/config:/config  # ← Change this
```

### 3. Set your ImmichFrame container name (if different from default)

By default, the editor looks for a container named `immichframe`. If yours has a different name, set it:

```bash
export IMMICHFRAME_CONTAINER=your-container-name
```

Or in docker-compose, uncomment and edit the environment variable:

```yaml
environment:
  - IMMICHFRAME_CONTAINER=${IMMICHFRAME_CONTAINER:-immichframe}
```

### 4. Run

```bash
docker compose up -d
```

Open `http://your-host:8081` in your browser.

> **Note:** Make sure your `Settings.yml` already has your Immich server URL and API key configured. The editor reads and updates the People and Albums selections — it doesn't set up Immich connection details.

## Configuration

The editor is configured via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `IMMICHFRAME_CONTAINER` | `immichframe` | Name of your ImmichFrame Docker container |
| `SETTINGS_FILE` | `/config/Settings.yml` | Path to ImmichFrame Settings.yml inside container |

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Flask Editor (port 8081)                           │
│  - app.py: Flask backend                           │
│  - templates/edit.html: Web UI                      │
│                                                     │
│  Reads: Settings.yml (ImmichFrame config)           │
│  Fetches: People/Albums from Immich API             │
│  Writes: Settings.yml + restarts ImmichFrame       │
└─────────────────────────────────────────────────────┘
          │
          │ saves config + restart
          ▼
┌─────────────────────────────────────────────────────┐
│  ImmichFrame (port 8080) — separate container        │
│  (not managed by this project)                     │
└─────────────────────────────────────────────────────┘
```

## Features

### People Selection
- Grid view with thumbnails fetched live from Immich
- Search to filter people by name
- Select All / Deselect All buttons
- Thumbnails cached in-memory for performance

### Album Selection
- Same grid interface as people
- Search and select/deselect all
- Leave all unchecked = show all photos

### Display Settings
- **Timing**: Slide interval, transition duration
- **Clock**: Show/hide, format
- **Display**: Photo date, album name, people names, location, weather
- **Layout**: Split view, center, left, right

## File Structure

```
immichframe-editor/
├── docker-compose.yml          # Container setup
├── LICENSE                    # MIT License
├── README.md                  # This file
├── .gitignore
├── app/
│   ├── app.py                 # Flask backend
│   └── templates/
│       └── edit.html          # Web UI (Jinja2 template)
└── config/
    └── Settings.yml.example   # Example Settings.yml for reference
```

## Contributing

Issues and PRs welcome! This was built to solve a specific pain point — editing YAML for a photo frame is tedious. Contributions to improve the UI, add features, or support more ImmichFrame options are all welcome.

## Credit

Built by [@PaulHammond](https://github.com/PaulHam211)

Based on:
- [Immich](https://immich.app) — self-hosted photo management
- [ImmichFrame](https://immichframe.dev) — digital photo frame for Immich
