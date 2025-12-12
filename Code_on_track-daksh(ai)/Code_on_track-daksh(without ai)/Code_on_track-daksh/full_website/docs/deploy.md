# Deployment Guide

This guide explains how to deploy the IRF QR Tracking System to production using Render and Docker Hub (or GHCR).

## Prerequisites

1.  **Docker Hub Account**: Create an account at [hub.docker.com](https://hub.docker.com/).
2.  **Render Account**: Create an account at [render.com](https://render.com/).
3.  **GitHub Secrets**: You need to set the following secrets in your GitHub repository settings (Settings > Secrets and variables > Actions):

### Required Secrets

| Secret Name | Description |
| :--- | :--- |
| `DOCKERHUB_USERNAME` | Your Docker Hub username. |
| `DOCKERHUB_TOKEN` | A Docker Hub Access Token (preferred over password). |
| `RENDER_API_KEY` | Create this in Render Account Settings > API Keys. |
| `RENDER_SERVICE_ID_BACKEND` | The ID of your Backend Web Service on Render (starts with `srv-`). |
| `RENDER_SERVICE_ID_FRONTEND` | The ID of your Frontend Web Service on Render (starts with `srv-`). |

### Optional Secrets

| Secret Name | Description |
| :--- | :--- |
| `GHCR_TOKEN` | If you prefer GitHub Container Registry, set this (usually a PAT). If set, Docker Hub is ignored. |
| `RENDER_JOB_ID_MIGRATE` | ID of a Render Job configured to run `alembic upgrade head`. If set, migrations run automatically. |

## Render Setup

### 1. Database (PostgreSQL)
1.  Create a **New PostgreSQL** database on Render.
2.  Note the **Internal Connection URL** (for backend service) and **External Connection URL** (for local access if needed).

### 2. Backend Service
1.  Create a **New Web Service**.
2.  Select "Deploy an existing image from a registry".
3.  Enter a placeholder image (e.g., `python:3.11`) initially, or build and push one manually first.
4.  **Name**: `irf-backend`
5.  **Region**: Same as Database.
6.  **Environment Variables**:
    *   `DATABASE_URL`: Paste the **Internal Connection URL** from the database step.
    *   `SECRET_KEY`: Generate a strong random string.
    *   `ALGORITHM`: `HS256`
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
    *   `CORS_ORIGINS`: The URL of your frontend service (e.g., `https://irf-frontend.onrender.com`).
7.  **Health Check Path**: `/healthz`

### 3. Frontend Service
1.  Create a **New Web Service**.
2.  Select "Deploy an existing image from a registry".
3.  **Name**: `irf-frontend`
4.  **Environment Variables**:
    *   `VITE_API_URL`: The URL of your backend service (e.g., `https://irf-backend.onrender.com`).
    *   **Note**: Since the frontend is built into a static image, `VITE_API_URL` must be available at **build time**. 
    *   *Correction*: The current Dockerfile builds the frontend. To support runtime configuration or build-time injection, you might need to update the workflow to pass build args. 
    *   **Workaround**: For now, ensure `VITE_API_URL` is set in the `frontend/.env` or passed as a build arg. The current setup assumes the API URL is known or relative. If it's a separate domain, you might need to rebuild with the correct URL.
    *   *Recommendation*: Add `VITE_API_URL` to the `docker build` command in the workflow if it changes per environment, or use a runtime config solution.

### 4. Migration Job (Optional but Recommended)
1.  Create a **New Job** on Render.
2.  Use the same Backend image.
3.  **Command**: `alembic upgrade head`
4.  **Environment Variables**: Same as Backend (`DATABASE_URL`, etc.).
5.  Get the **Job ID** from the URL or settings and save it as `RENDER_JOB_ID_MIGRATE` in GitHub Secrets.

## Triggering Deployment

- **Automatic**: Push to the `main` branch.
- **Manual**: Go to GitHub Actions > "Deploy to Production" > "Run workflow".

## Troubleshooting

- **Database Connection**: Ensure the backend service is in the same region as the database and uses the internal URL.
- **CORS Errors**: Ensure `CORS_ORIGINS` in backend matches the frontend URL exactly (no trailing slash).
- **Frontend API Calls**: If frontend cannot reach backend, check the Network tab. If it's trying to hit `localhost`, you need to rebuild the frontend image with the correct `VITE_API_URL`.

## Safe Deploy Flow

The deployment workflow includes safety checks:

1.  **Migrations First**: The workflow runs `alembic upgrade head` via a Render Job *before* deploying the new code.
    *   **Requirement**: You MUST create a Job on Render (Command: `alembic upgrade head`) and save its ID as `RENDER_JOB_ID_MIGRATE`.
    *   If this secret is missing, the deploy will fail to prevent schema mismatches.

2.  **Smoke Tests**: After deployment, the workflow runs basic checks against the live environment.
    *   **Requirement**: Set the following secrets:
        *   `DEPLOY_BACKEND_URL`: Full URL of your backend (e.g., `https://irf-backend.onrender.com`).
        *   `TEST_ADMIN_USERNAME`: Username of an admin user for testing.
        *   `TEST_ADMIN_PASSWORD`: Password for the test admin.
    *   The tests check `/healthz`, `/auth/login`, and `/reports/summary`.
    *   If tests fail, the workflow fails (and you should manually rollback on Render dashboard).

