# Sematica
## Desktop application for managing semantic web knowledge bases


# I -  Pre-requisites
## 1- System dependencies
### Linux :
```bash
sudo apt update
sudo apt install libwebkit2gtk-4.1-dev \
  build-essential \
  curl \
  wget \
  file \
  libxdo-dev \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev
```
### Windows :
Tauri uses the Microsoft C++ Build Tools for development as well as Microsoft Edge WebView2. These are both required for development on Windows.
#### Microsoft C++ Build Tools
- Download the [Microsoft C++ Build Tools installer](https://visualstudio.microsoft.com/fr/visual-cpp-build-tools/) and open it to begin installation.
- During installation check the “Desktop development with C++” option

#### WebView2
- Install WebView2 by visiting the [Microsoft Edge WebView2 installer](https://developer.microsoft.com/en-us/microsoft-edge/webview2/?form=MA13LH#download-section). Download the “Evergreen Bootstrapper” and install it.


## 2- Rust and cargo 
### Linux 
```bash
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```
### Windows
in Powershell (run as administrator)
```Powershell
winget install --id Rustlang.Rustup
```
## 3- Node.js

## 4- Python 

## 5- UV - Python package manager
### Linux 
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### Windows
```Powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```


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

## III - Development workflow

1. Start the backend server
```bash
cd backend
uvicorn main:app --reload --port 8000
```
2. Start the Tauri application
```bash
cargo tauri dev
```


## IV - build for production 
```bash
# 1. Compile FastAPI to binary
cd backend && pyinstaller --onefile --name backend-server main.py
cp dist/backend-server ../src-tauri/binaries/backend-server-<target-triple>

# 2. Build the full app
cargo tauri build
# Output: src-tauri/target/release/bundle/
```