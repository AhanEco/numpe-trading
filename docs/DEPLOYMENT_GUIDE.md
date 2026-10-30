# NUMPE TRADING SOFTWARE – Deployment Guide

This guide describes how to deploy **NUMPE TRADING SOFTWARE** to the public internet so it can be opened from any mobile phone, tablet, or desktop using a shareable HTTPS URL.

---

## 1. Architecture Overview

The system consists of:
1. **Frontend:** React + TypeScript + Vite + Tailwind CSS (Responsive mobile-friendly PWA).
2. **Backend:** FastAPI (Python 3.12/3.14) with Async SQLAlchemy, Pandas, and APScheduler.
3. **Database:** PostgreSQL (Supabase / Render / Railway) or SQLite for lightweight hosting.
4. **Automated Scheduler:** Background task runner updating daily prices post-market close (15:45 IST) and streaming financial news every hour.

---

## 2. Option A: 1-Click Deployment on Render / Railway (Recommended)

Render and Railway can build and run the multi-stage Docker container located in the repository root. This hosts **both** the backend API and the React frontend on a single free or low-cost service with an automatic free HTTPS URL (`https://your-app.onrender.com`).

### Steps:
1. Push this repository to your GitHub account:
   ```bash
   git init
   git add .
   git commit -m "Deploy NUMPE Trading Software"
   git remote add origin https://github.com/<your-username>/numpe-trading.git
   git push -u origin main
   ```
2. Log in to [Render](https://render.com) or [Railway](https://railway.app).
3. Click **New +** -> **Web Service**.
4. Connect your GitHub repository.
5. Select **Docker** as the runtime (Render will automatically detect the root `Dockerfile`).
6. Set the Environment Variables:
   * `SECRET_KEY`: `<generate-a-secure-random-32-char-string>`
   * `ADMIN_PASSWORD`: `<your-admin-password>`
   * `PORT`: `8000`
   * `CORS_ORIGINS`: `*`
   * `DATABASE_URL`: `sqlite+aiosqlite:///./numpe.db` (or your Supabase PostgreSQL connection string)
7. Click **Deploy Web Service**.
8. In 2–3 minutes, your live web application will be live at `https://numpe-trading.onrender.com`!

---

## 3. Option B: Vercel (Frontend) + Render / Railway (Backend)

If you prefer deploying the React frontend on Vercel:

### 1. Deploy the Backend:
* Deploy the `backend/` folder on Render or Railway as a Python Web Service.
* Build Command: `pip install -r requirements.txt`
* Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
* Note down your backend URL: e.g. `https://numpe-api.onrender.com`.

### 2. Deploy Frontend on Vercel:
* Import the repository on [Vercel](https://vercel.com).
* Root Directory: `frontend`
* Framework Preset: `Vite`
* Environment Variables:
  * `VITE_API_URL`: `https://numpe-api.onrender.com`
* Click **Deploy**. Vercel will provide your HTTPS URL (e.g. `https://numpe-trading.vercel.app`).

---

## 4. Option C: Using Managed Supabase PostgreSQL

To switch from SQLite to Supabase PostgreSQL:
1. Create a free project at [Supabase](https://supabase.com).
2. Go to **Project Settings** -> **Database** -> **Connection string** (URI).
3. Select the **AsyncPG / Python** format:
   ```
   postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
   ```
4. Update the `DATABASE_URL` environment variable on your hosting provider.
5. FastAPI will automatically create all tables on startup.

---

## 5. Mobile & Tablet Progressive Web App (PWA) Setup

NUMPE is designed to be installed as an app on your father's phone or tablet:

* **On iPhone / iPad (Safari):**
  1. Open the shareable HTTPS URL in Safari.
  2. Tap the **Share** button (box with upward arrow) at the bottom.
  3. Scroll down and tap **Add to Home Screen**.
  4. The **NUMPE** app icon will appear on the home screen and open full-screen like a native application!

* **On Android (Chrome):**
  1. Open the HTTPS URL in Chrome.
  2. Tap the three-dot menu in the top right.
  3. Tap **Install app** or **Add to Home Screen**.

