# Local Image Effects (Docker)

Streamlit app that applies image effects (grayscale, blur, sharpen, etc.) using only **Streamlit** and **Pillow**. No AWS or other credentials required.

## Purpose

This project serves to:

- **Run a simple app locally** — Upload an image, apply an effect, download the result. No cloud or API keys.
- **Compare container build strategies** — Same app built in different ways: single-stage, distroless multistage, and Chainguard multistage.
- **Practice secure, minimal images** — Use smaller, hardened bases (distroless, Chainguard) to reduce attack surface and dependency count.
- **Integrate with Docker Scout** — Scan images for vulnerabilities (CVEs), view SBOMs, and get base-image update recommendations.

## Contents

| File | Description |
|------|-------------|
| `app.py` | Streamlit app: upload image, choose effect, download result |
| `Dockerfile` | Single-stage build (python:3.11-slim) |
| `Dockerfile.distroless` | Multistage build; final stage is Google distroless (no shell, no pip) |
| `Dockerfile.chainguard` | Multistage build; final stage is Chainguard minimal Python image |

## Build & run

### Option 1: Single-stage (`Dockerfile`)

```bash
docker build -t distroles-app .
docker run -p 8501:8501 distroles-app
```

With a version tag:

```bash
docker build -t distroles-app:2 .
docker run -p 8501:8501 distroles-app:2
```

### Option 2: Multistage distroless (`Dockerfile.distroless`)

Smaller final image; no shell or pip in the running container:

```bash
docker build -f Dockerfile.distroless -t distroles-app:2 .
docker run -p 8501:8501 distroles-app:2
```

### Option 3: Multistage Chainguard (`Dockerfile.chainguard`)

Uses Chainguard’s minimal Python image (hardened, small footprint):

```bash
docker build -f Dockerfile.chainguard -t distroles-app:chainguard .
docker run -p 8501:8501 distroles-app:chainguard
```

**Note:** Use the same image name when building and running. If you see "pull access denied", the name at build time (e.g. `distroles-app:chainguard`) must match the one in `docker run`.

## Security

### Why multiple Dockerfiles

- **Single-stage (`Dockerfile`)** — Easiest to build and debug; includes a full slim OS and pip. Good for local dev.
- **Distroless (`Dockerfile.distroless`)** — Final image has no shell, no package manager. Fewer tools for an attacker; fewer packages to patch.
- **Chainguard (`Dockerfile.chainguard`)** — Minimal, curated base with a small set of packages and a focus on low CVE count. Often shows **0 Critical/High/Medium/Low** in Scout when the base is well maintained.

Choosing distroless or Chainguard reduces the number of components in the running container and aligns with “minimal image” best practices.

### Scanning with Docker Scout

[Docker Scout](https://docs.docker.com/scout/) provides vulnerability reporting and SBOMs. You need to be logged in: `docker login`.

**Quick overview of an image:**

```bash
docker scout quickview <image-name>:<tag>
# or by image ID
docker scout quickview <image-id>
```

**Understanding quickview:**

- **0C 1H 2M 21L** = 0 Critical, 1 High, 2 Medium, 21 Low (example for a python:3.11-slim–based image).
- **0C 0H 0M 0L** = No known vulnerabilities in the indexed packages (often seen with Chainguard-based images).
- Scout also shows **base image** and **updated base image** suggestions (e.g. switch to `python:3.14-slim` to reduce CVEs).

**Useful Scout commands:**

| Command | Purpose |
|--------|--------|
| `docker scout quickview <image>` | Summary: CVEs and base image |
| `docker scout cves <image>` | List CVEs in detail |
| `docker scout recommendations <image>` | Base image update recommendations |

**Provenance (optional):** For more accurate base detection and supply-chain info, build with [BuildKit provenance](https://docs.docker.com/build/attestations/slsa-provenance/), e.g.:

```bash
docker build --provenance=true -f Dockerfile.distroless -t distroles-app:2 .
```

### SBOM and attestations

- Scout uses a **cached SBOM** (Software Bill of Materials) for the image — the “packages indexed” count (e.g. 179 vs 92) reflects how many components each image has; smaller/minimal images typically have fewer.
- Enabling **provenance attestations** (`--provenance=true`) improves base image detection and supports supply-chain and policy use cases.

## Run locally (no Docker)

```bash
pip install streamlit Pillow
streamlit run app.py
```

Then open http://localhost:8501.

## App behavior

- **Upload** an image (jpg, jpeg, png).
- **Choose effect:** None, Grayscale, Blur, Sharpen, Contrast, Brightness, or Small (256px).
- **Download** the result as PNG.

All processing is local; no external APIs or credentials.
