# Frontend demo (Vite + React)

This is a minimal Vite React demo app that showcases the dictionary search and translation demo.

Run locally:

```powershell
cd frontend\demo
npm install
npm run dev
# open http://localhost:5173
```

If your backend API is not at `http://127.0.0.1:8000`, set `VITE_API_BASE` before running:

```powershell
# Windows PowerShell temporary env:
$env:VITE_API_BASE='http://your-api-host:8000'
npm run dev
```
