#[cfg_attr(mobile, tauri::mobile_entry_point)]



pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let handle = app.handle().clone();

            // Spawn FastAPI sidecar in production
            #[cfg(not(debug_assertions))]
            {
                tauri::async_runtime::spawn(async move {
                    let sidecar = handle
                        .shell()
                        .sidecar("backend-server")
                        .expect("Failed to find backend-server sidecar")
                        .spawn()
                        .expect("Failed to spawn backend-server");

                    // Keep sidecar alive
                    let _ = sidecar;
                });
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}