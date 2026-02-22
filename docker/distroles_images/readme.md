# Local Image Effects (Docker)

Streamlit app that applies image effects (grayscale, blur, sharpen, etc.) using only **Streamlit** and **Pillow**. No AWS or other credentials required.

## Contents

| File | Description |
|------|-------------|
| `app.py` | Streamlit app: upload image, choose effect, download result |
| `Dockerfile` | Single-stage build (python:3.11-slim) |
| `Dockerfile.distroless` | Multistage build with distroless final image |

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

Smaller, more minimal final image (no shell, no pip in the running container):

```bash
docker build -f Dockerfile.distroless -t distroles-app:2 .
docker run -p 8501:8501 distroles-app:2
```

**Note:** Use the same image name when building and running (e.g. `distroles-app` or `distroles-app:2`). If you see "pull access denied", the image name at build time was different from the one you used in `docker run`.

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
