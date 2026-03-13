

## IV - build for production 
```bash
# 1. Compile FastAPI to binary
cd backend && pyinstaller backend-server.spec
cp dist/backend-server ../src-tauri/binaries/backend-server-x86_64-unknown-linux-gnu

# 2. Build the full app
cargo tauri build
# Output: src-tauri/target/release/bundle/
```