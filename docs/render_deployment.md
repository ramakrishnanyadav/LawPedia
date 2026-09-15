# LawPedia — Render.com Hosting & Deployment Guide

This guide provides step-by-step instructions for hosting LawPedia on **Render.com** using the included [`render.yaml`](../render.yaml) blueprint or as a Docker container.

---

## 🚀 Option 1: 1-Click Render Blueprint Deployment (Recommended)

Render Blueprints automatically set up the web service, build commands, start commands, health probes, and environment variables.

### Steps:
1. Push your repository to **GitHub** or **GitLab**.
2. Log into your [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Blueprint**.
4. Connect your `LawPedia` GitHub repository.
5. Render will automatically detect [`render.yaml`](../render.yaml) and populate the configuration:
   - **Service Name**: `lawpedia-platform`
   - **Build Command**: `cd frontend && npm install && npm run build && cd .. && pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
6. Click **Apply**. Render will build the frontend assets, install Python dependencies, and launch the unified server.

---

## 🐳 Option 2: Render Docker Web Service Deployment

Render supports hosting directly from the repository's [`Dockerfile`](../Dockerfile).

### Steps:
1. On the Render Dashboard, click **New +** -> **Web Service**.
2. Connect your repository.
3. Select **Docker** as the Environment.
4. Set the runtime environment variables:
   - `ENV`: `production`
   - `DEBUG`: `False`
   - `LAWPEDIA_DEMO_MODE`: `true`
   - `LAWPEDIA_DEMO_TOKEN`: `lawpedia_demo_token_2026`
   - `LAWPEDIA_SECRET_KEY`: `a-secure-random-secret-key-for-production`
5. Click **Create Web Service**.

---

## 🛠 Required Environment Variables Reference

| Variable Name | Required | Default / Example Value | Description |
| :--- | :--- | :--- | :--- |
| `ENV` | Yes | `production` | Set to `production` for cloud deployment |
| `DEBUG` | Yes | `False` | Must be `False` in production (enforced by startup check) |
| `LAWPEDIA_DEMO_MODE` | No | `true` | Enables demonstration token access mode |
| `LAWPEDIA_DEMO_TOKEN` | No | `lawpedia_demo_token_2026` | Auth token for demo evaluation |
| `LAWPEDIA_SECRET_KEY` | Yes | `<random 32-char string>` | Secret key for cryptographic operations |
| `LAWPEDIA_LIGHTWEIGHT_MODE` | No | `true` | Prevents 512MB RAM OOM on Render Free Tier by using 384-dim TF-IDF vectorizer |
| `OPENAI_API_KEY` | No | `sk-...` | Optional key for OpenAI LLM simplification |
| `ANTHROPIC_API_KEY` | No | `sk-ant-...` | Optional key for Anthropic Claude simplification |

---

## 🔍 Verification & Health Checks

Once deployed, verify your deployment endpoints:
- **Web App Interface**: `https://<your-app>.onrender.com/`
- **Liveness Health Check**: `https://<your-app>.onrender.com/health`
- **Readiness Probe**: `https://<your-app>.onrender.com/ready`
- **Interactive Swagger Docs**: `https://<your-app>.onrender.com/docs`
