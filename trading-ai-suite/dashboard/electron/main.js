// Trading AI Suite — Electron Main Process
// Wraps the Next.js static export inside a native desktop window.

const { app, BrowserWindow } = require("electron");
const path = require("path");
const serve = require("electron-serve");

// Serve the Next.js static export from the "out" directory
const loadURL = serve({ directory: path.join(__dirname, "..", "out") });

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    backgroundColor: "#131722",
    title: "Trading AI Suite",
    icon: path.join(__dirname, "..", "public", "favicon.ico"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    // Frameless look with native title bar
    titleBarStyle: "hiddenInset",
    autoHideMenuBar: true,
  });

  // Load the static export via serve protocol
  loadURL(mainWindow);

  // Open DevTools in development
  if (process.env.NODE_ENV === "development") {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on("closed", () => {
    mainWindow = null;
  });
}

// ─── App Lifecycle ─────────────────────────
app.on("ready", createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (mainWindow === null) {
    createWindow();
  }
});

// Set app name
app.setName("Trading AI Suite");
