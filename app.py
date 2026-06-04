"""Cloudsmith Demo Flask Application."""

import os
import platform
import socket
from datetime import datetime

from flask import Flask, jsonify

app = Flask(__name__)

# Track request count for demo purposes
request_count = 0

# Build metadata from Docker build args / environment
BUILD_NUMBER = os.environ.get("BUILD_NUMBER", "dev")
BUILD_DATE = os.environ.get("BUILD_DATE", "local build")
GIT_SHA = os.environ.get("GIT_SHA", "unknown")
CLOUDSMITH_WORKSPACE = os.environ.get("CLOUDSMITH_WORKSPACE", "dmk-software-solutions")
CLOUDSMITH_REPOSITORY = os.environ.get("CLOUDSMITH_REPOSITORY", "oss-oidc-test")


def get_system_info():
    """Gather system information for display."""
    return {
        "hostname": socket.gethostname(),
        "platform": platform.system(),
        "platform_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.machine(),
    }


def get_installed_packages():
    """Return a list of installed Python packages."""
    packages = []
    try:
        from importlib.metadata import distributions

        for dist in distributions():
            packages.append({"name": dist.metadata["Name"], "version": dist.version})
        packages.sort(key=lambda p: p["name"].lower())
    except Exception:
        packages = [{"name": "Unable to read packages", "version": "N/A"}]
    return packages


@app.route("/")
def index():
    """Render the main demo page."""
    global request_count
    request_count += 1

    info = get_system_info()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    packages = get_installed_packages()
    git_sha_short = GIT_SHA[:7] if len(GIT_SHA) > 7 else GIT_SHA
    image_tag = f"flask-app:{BUILD_NUMBER}"
    cloudsmith_package_url = (
        f"https://app.cloudsmith.com/{CLOUDSMITH_WORKSPACE}/r/{CLOUDSMITH_REPOSITORY}/"
    )

    # Build dependency rows
    dep_rows = ""
    for pkg in packages:
        dep_rows += f"""
                    <tr>
                        <td>{pkg['name']}</td>
                        <td><span class="version-badge">{pkg['version']}</span></td>
                    </tr>"""

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cloudsmith Flask Demo</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
                min-height: 100vh;
                color: #fff;
                padding: 2rem;
            }}
            .container {{
                max-width: 960px;
                margin: 0 auto;
            }}
            header {{
                text-align: center;
                margin-bottom: 2rem;
            }}
            .logo {{
                font-size: 3rem;
                font-weight: 700;
                background: linear-gradient(90deg, #00d4ff, #7b2cbf);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 0.25rem;
            }}
            .subtitle {{
                color: #a0a0a0;
                font-size: 1.1rem;
            }}
            .version-banner {{
                display: inline-flex;
                align-items: center;
                gap: 0.75rem;
                background: rgba(0, 212, 255, 0.15);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 20px;
                padding: 0.4rem 1rem;
                margin-top: 0.75rem;
                font-size: 0.9rem;
            }}
            .version-banner a {{
                color: #00d4ff;
                text-decoration: none;
                font-weight: 500;
            }}
            .version-banner a:hover {{
                text-decoration: underline;
            }}
            .card {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 16px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            .card h2 {{
                color: #00d4ff;
                margin-bottom: 1rem;
                font-size: 1.3rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
            }}
            .info-item {{
                background: rgba(0, 212, 255, 0.1);
                padding: 1rem;
                border-radius: 8px;
            }}
            .info-label {{
                color: #888;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            .info-value {{
                color: #fff;
                font-size: 1.1rem;
                font-weight: 500;
                margin-top: 0.25rem;
                word-break: break-all;
            }}

            /* Pipeline */
            .pipeline {{
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0;
                padding: 1rem 0;
            }}
            .pipeline-step {{
                background: rgba(0, 212, 255, 0.1);
                border: 1px solid rgba(0, 212, 255, 0.25);
                border-radius: 10px;
                padding: 0.6rem 0.75rem;
                text-align: center;
                flex: 1 1 0;
                min-width: 0;
            }}
            .pipeline-step .step-label {{
                font-size: 0.7rem;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            .pipeline-step .step-value {{
                font-weight: 600;
                margin-top: 0.2rem;
                font-size: 0.85rem;
            }}
            .pipeline-arrow {{
                color: #00d4ff;
                font-size: 1.2rem;
                padding: 0 0.15rem;
                flex-shrink: 0;
            }}

            /* Dependencies table */
            .dep-table {{
                width: 100%;
                border-collapse: collapse;
                max-height: 260px;
                display: block;
                overflow-y: auto;
            }}
            .dep-table thead {{
                position: sticky;
                top: 0;
                background: #16213e;
            }}
            .dep-table th {{
                text-align: left;
                padding: 0.5rem 0.75rem;
                color: #888;
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                border-bottom: 1px solid rgba(255,255,255,0.1);
            }}
            .dep-table td {{
                padding: 0.4rem 0.75rem;
                border-bottom: 1px solid rgba(255,255,255,0.05);
                font-size: 0.9rem;
            }}
            .dep-source {{
                color: #00d4ff;
                font-size: 0.8rem;
                margin-top: 0.75rem;
            }}
            .dep-source a {{
                color: #00d4ff;
            }}
            .version-badge {{
                background: rgba(123, 44, 191, 0.3);
                padding: 0.15rem 0.5rem;
                border-radius: 10px;
                font-size: 0.85rem;
                font-family: monospace;
            }}

            .endpoints {{
                display: flex;
                flex-wrap: wrap;
                gap: 0.75rem;
            }}
            .endpoint {{
                background: linear-gradient(135deg, #7b2cbf, #00d4ff);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                text-decoration: none;
                color: #fff;
                font-weight: 500;
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            .endpoint:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
            }}
            .status {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }}
            .status-dot {{
                width: 10px;
                height: 10px;
                background: #00ff88;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }}
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.5; }}
            }}
            .counter {{
                font-size: 2.5rem;
                font-weight: 700;
                color: #00d4ff;
            }}
            footer {{
                text-align: center;
                margin-top: 3rem;
                color: #666;
            }}
            footer a {{
                color: #00d4ff;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <div class="logo">Cloudsmith</div>
                <p class="subtitle">Flask Demo Application</p>
                <div class="version-banner">
                    <span>{image_tag}</span>
                    <span style="color:#555;">|</span>
                    <span>sha: <code>{git_sha_short}</code></span>
                    <span style="color:#555;">|</span>
                    <a href="{cloudsmith_package_url}" target="_blank">View in Cloudsmith</a>
                </div>
            </header>

            <div class="card">
                <h2><span class="status"><span class="status-dot"></span></span> Application Status</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Status</div>
                        <div class="info-value">Running</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Server Time</div>
                        <div class="info-value">{current_time}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Page Views</div>
                        <div class="info-value counter">{request_count}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Build Date</div>
                        <div class="info-value">{BUILD_DATE}</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Supply Chain Pipeline</h2>
                <div class="pipeline">
                    <div class="pipeline-step">
                        <div class="step-label">Source</div>
                        <div class="step-value">GitHub</div>
                    </div>
                    <div class="pipeline-arrow">&rarr;</div>
                    <div class="pipeline-step">
                        <div class="step-label">Test</div>
                        <div class="step-value">pytest</div>
                    </div>
                    <div class="pipeline-arrow">&rarr;</div>
                    <div class="pipeline-step">
                        <div class="step-label">Dependencies</div>
                        <div class="step-value">Cloudsmith Python</div>
                    </div>
                    <div class="pipeline-arrow">&rarr;</div>
                    <div class="pipeline-step">
                        <div class="step-label">Base Image</div>
                        <div class="step-value">Chainguard</div>
                    </div>
                    <div class="pipeline-arrow">&rarr;</div>
                    <div class="pipeline-step">
                        <div class="step-label">Registry</div>
                        <div class="step-value">Cloudsmith Docker</div>
                    </div>
                    <div class="pipeline-arrow">&rarr;</div>
                    <div class="pipeline-step" style="border-color: #00ff88;">
                        <div class="step-label">Running</div>
                        <div class="step-value" style="color: #00ff88;">This App</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Container Information</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <div class="info-label">Hostname</div>
                        <div class="info-value">{info['hostname']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Platform</div>
                        <div class="info-value">{info['platform']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Architecture</div>
                        <div class="info-value">{info['architecture']}</div>
                    </div>
                    <div class="info-item">
                        <div class="info-label">Python Version</div>
                        <div class="info-value">{info['python_version']}</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Python Dependencies</h2>
                <table class="dep-table">
                    <thead>
                        <tr>
                            <th>Package</th>
                            <th>Version</th>
                        </tr>
                    </thead>
                    <tbody>{dep_rows}
                    </tbody>
                </table>
                <p class="dep-source">
                    Installed from
                    <a href="https://app.cloudsmith.com/{CLOUDSMITH_WORKSPACE}/r/{CLOUDSMITH_REPOSITORY}/"
                       target="_blank">
                        cloudsmith.io/{CLOUDSMITH_WORKSPACE}/{CLOUDSMITH_REPOSITORY}
                    </a>
                </p>
            </div>

            <div class="card">
                <h2>API Endpoints</h2>
                <div class="endpoints">
                    <a href="/health" class="endpoint">GET /health</a>
                    <a href="/api/info" class="endpoint">GET /api/info</a>
                    <a href="/api/stats" class="endpoint">GET /api/stats</a>
                    <a href="/api/sbom" class="endpoint">GET /api/sbom</a>
                </div>
            </div>

            <footer>
                <p>Built with Flask &bull; Deployed via <a href="https://cloudsmith.com">Cloudsmith</a></p>
            </footer>
        </div>
    </body>
    </html>
    """
    return html


@app.route("/health")
def health():
    """Health check endpoint for container orchestration."""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


@app.route("/api/info")
def api_info():
    """Return system information as JSON."""
    info = get_system_info()
    info["timestamp"] = datetime.now().isoformat()
    info["build_number"] = BUILD_NUMBER
    info["build_date"] = BUILD_DATE
    info["git_sha"] = GIT_SHA
    return jsonify(info)


@app.route("/api/stats")
def api_stats():
    """Return application statistics."""
    return jsonify(
        {
            "request_count": request_count,
            "version": "1.0.0",
            "build_number": BUILD_NUMBER,
        }
    )


@app.route("/api/sbom")
def api_sbom():
    """Return a software bill of materials for this application."""
    packages = get_installed_packages()
    return jsonify(
        {
            "format": "cloudsmith-sbom-lite",
            "generated_at": datetime.now().isoformat(),
            "build_number": BUILD_NUMBER,
            "git_sha": GIT_SHA,
            "source_repo": f"{CLOUDSMITH_WORKSPACE}/{CLOUDSMITH_REPOSITORY}",
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "packages": packages,
        }
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
