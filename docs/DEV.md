
## III - Development workflow

1. Start the backend server

```bash
cd backend
uvicorn main:app --reload --port 8000
```
2. Start the frontend

```bash
npm run dev
```

if you want to test the desktop app start tauri :
```bash
cargo tauri dev
```
