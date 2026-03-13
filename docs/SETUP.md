
# II - Project Setup
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
cd /app/storage/database && touch database.db
```
3. compile fastAPI to binary
```bash
cd backend
pyinstaller backend-server.spec
```
4. Register the sidecar in Tauri
```bash
# Get your target triple:
rustc -vV | grep host
# e.g: host: x86_64-unknown-linux-gnu

cp backend/dist/backend-server src-tauri/binaries/backend-server-x86_64-unknown-linux-gnu
```