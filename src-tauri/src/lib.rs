use tauri::{AppHandle, Manager, WebviewUrl, WebviewWindowBuilder};
use tauri_plugin_shell::ShellExt;
use tauri_plugin_shell::process::CommandEvent;

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

            let handle = app.handle().clone();

            tauri::async_runtime::spawn(async move {
                println!("[sidecar] attempting to spawn backend-server...");

                let sidecar_cmd = match handle.shell().sidecar("backend-server") {
                    Ok(cmd) => cmd,
                    Err(e) => {
                        eprintln!("[sidecar] FATAL: could not find backend-server binary: {}", e);
                        return;
                    }
                };

                let (mut rx, _child) = match sidecar_cmd.spawn() {
                    Ok(result) => {
                        println!("[sidecar] spawned successfully");
                        result
                    }
                    Err(e) => {
                        eprintln!("[sidecar] FATAL: failed to spawn: {}", e);
                        return;
                    }
                };

                // Stream logs from sidecar in a separate task
                tauri::async_runtime::spawn(async move {
                    while let Some(event) = rx.recv().await {
                        match event {
                            CommandEvent::Stdout(line) => {
                                println!("[backend] {}", String::from_utf8_lossy(&line));
                            }
                            CommandEvent::Stderr(line) => {
                                eprintln!("[backend] {}", String::from_utf8_lossy(&line));
                            }
                            CommandEvent::Error(e) => {
                                eprintln!("[backend] process error: {}", e);
                            }
                            CommandEvent::Terminated(status) => {
                                eprintln!("[backend] TERMINATED — code: {:?}, signal: {:?}",
                                    status.code, status.signal);
                            }
                            _ => {}
                        }
                    }
                });

                // Poll health endpoint — 60 attempts × 500ms = 30s timeout
                println!("[sidecar] waiting for FastAPI to be ready...");
                let client = reqwest::Client::builder()
                    .timeout(std::time::Duration::from_secs(2))
                    .build()
                    .unwrap();

                let mut ready = false;
                for attempt in 1..=60 {
                    match client.get("http://127.0.0.1:8000/health").send().await {
                        Ok(res) => {
                            println!("[sidecar] backend ready! HTTP {}", res.status());
                            ready = true;
                            break;
                        }
                        Err(e) => {
                            eprintln!("[sidecar] attempt {}/60 — not ready: {}", attempt, e);
                            tokio::time::sleep(std::time::Duration::from_millis(500)).await;
                        }
                    }
                }

                if !ready {
                    eprintln!("[sidecar] FATAL: backend never became ready after 30s");
                    // Still close splash so app isn't frozen — user will see API errors
                }

                // Transition: close splash, show main
                if let Some(splash) = handle.get_webview_window("splashscreen") {
                    let _ = splash.close();
                }
                if let Some(main) = handle.get_webview_window("main") {
                    let _ = main.show();
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}