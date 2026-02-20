use tauri::{AppHandle, Manager, WebviewWindowBuilder, WebviewUrl};

#[tauri::command]
fn splash_screen(app: AppHandle) -> Result<(), String> {
    if let Some(splash) = app.get_webview_window("splashscreen") {
        let _ = splash.close();
    }
    if let Some(main) = app.get_webview_window("main") {
        main.show().map_err(|e| e.to_string())?;
    }
    Ok(())
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![splash_screen])
        .setup(|app| {
            let resource_path = app
                .path()
                .resource_dir()
                .expect("Failed to get resource dir")
                .join("splashscreen.html");

            let splash_url = WebviewUrl::External(
                format!("file://{}", resource_path.to_str().unwrap())
                    .parse()
                    .unwrap(),
            );

            WebviewWindowBuilder::new(app, "splashscreen", splash_url)
                .title("Semantica")
                .inner_size(1200.0, 800.0)
                .center()
                .always_on_top(true)
                .build()
                .expect("Failed to create splashscreen window");

            #[cfg(not(debug_assertions))]
            {
                let handle = app.handle().clone();
                tauri::async_runtime::spawn(async move {
                    let sidecar = handle
                        .shell()
                        .sidecar("backend-server")
                        .expect("Failed to find backend-server sidecar")
                        .spawn()
                        .expect("Failed to spawn backend-server");
                    let _ = sidecar;
                });
            }

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}