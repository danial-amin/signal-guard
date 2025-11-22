import os

PROJECT_ROOT = "signalguard-observability"

# List of directories to create (relative to project root)
DIRS = [
    "services/app/static",
    "services/anomaly-detector",
    "observability/prometheus",
    "observability/grafana/provisioning/datasources",
    "observability/grafana/provisioning/dashboards",
    "observability/grafana/dashboards",
]

# Files to create (relative to project root) with minimal placeholder content
FILES = {
    "docker-compose.yml": "# TODO: paste docker-compose.yml content here\n",
    "services/app/requirements.txt": "# TODO: paste app requirements.txt here\n",
    "services/app/Dockerfile": "# TODO: paste app Dockerfile here\n",
    "services/app/app.py": "# TODO: paste app.py here\n",
    "services/app/static/index.html": "<!-- TODO: paste index.html here -->\n",
    "services/app/static/styles.css": "/* TODO: paste styles.css here */\n",
    "services/app/static/script.js": "// TODO: paste script.js here\n",
    "services/anomaly-detector/requirements.txt": "# TODO: paste anomaly-detector requirements.txt here\n",
    "services/anomaly-detector/Dockerfile": "# TODO: paste anomaly-detector Dockerfile here\n",
    "services/anomaly-detector/detector.py": "# TODO: paste detector.py here\n",
    "observability/prometheus/prometheus.yml": "# TODO: paste prometheus.yml here\n",
    "observability/grafana/provisioning/datasources/datasource.yml": "# TODO: paste Grafana datasource.yml here\n",
    "observability/grafana/provisioning/dashboards/dashboard.yml": "# TODO: paste Grafana dashboard.yml here\n",
    "observability/grafana/dashboards/signalguard-dashboard.json": "{\n  \"_comment\": \"TODO: paste signalguard-dashboard.json here\"\n}\n",
    "README.md": "# SignalGuard Observability\n\nTODO: fill in project description.\n",
    ".gitignore": "# Basic Python & Docker ignores\n__pycache__/\n*.pyc\n.env\n.idea/\n.vscode/\n*.log\n",
}


def create_dirs():
    for d in DIRS:
        path = os.path.join(PROJECT_ROOT, d)
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")


def create_files():
    for rel_path, content in FILES.items():
        path = os.path.join(PROJECT_ROOT, rel_path)
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Only create/overwrite if file does not exist or is empty
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created file: {path}")
        else:
            print(f"Skipped (already exists, non-empty): {path}")


def main():
    print(f"Initializing project structure in ./{PROJECT_ROOT}")
    os.makedirs(PROJECT_ROOT, exist_ok=True)
    create_dirs()
    create_files()
    print("\nDone. Now paste the respective code into each file.")
    print(f"Project root: ./{PROJECT_ROOT}")


if __name__ == "__main__":
    main()
