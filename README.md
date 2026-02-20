# Sematica
## Desktop application for managing semantic web knowledge bases


# Pre-requisites
- Rust 
- Cargo
- Node.js
- Python 3.10 or higher
- uv (recommended)

# Project Setup
1. Clone the repository
```bash
git clone https://github.com/afadel151/semantica.git
cd semantica
```
2. Install dependencies
```bash
cd frontend
npm install
cd ../backend
uv sync 
```
3. compile fastAPI to binary
```bash
cd backend
pyinstaller --onefile --name backend-server main.py
```
4. Register the sidecar in Tauri
```bash
# Get your target triple:
rustc -vV | grep host
# e.g: host: x86_64-unknown-linux-gnu

cp backend/dist/backend-server src-tauri/binaries/backend-server-x86_64-unknown-linux-gnu
```

## Development workflow

1. Start the backend server
```bash
cd backend
uvicorn main:app --reload --port 8000
```
2. Start the Tauri application
```bash
cargo tauri dev
```


## build for production 
```bash
# 1. Compile FastAPI to binary
cd backend && pyinstaller --onefile --name backend-server main.py
cp dist/backend-server ../src-tauri/binaries/backend-server-<target-triple>

# 2. Build the full app
cargo tauri build
# Output: src-tauri/target/release/bundle/
```