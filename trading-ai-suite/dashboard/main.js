const { app, BrowserWindow, Menu, Tray, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Determine if we're running in production (packaged) or development
const isDev = !app.isPackaged;
const PORT = 3000;

let mainWindow;
let nextProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'The Uprising Trading Floor',
    icon: path.join(__dirname, 'public', 'favicon.ico'),
    backgroundColor: '#0a0a0a',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
    },
    show: false, // Show when ready to avoid flash
  });

  // Remove default menu for production
  if (!isDev) {
    Menu.setApplicationMenu(null);
  }

  // Load the Next.js app
  const url = `http://localhost:${PORT}`;
  
  mainWindow.loadURL(url);

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Open external links in the default browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http')) {
      shell.openExternal(url);
    }
    return { action: 'deny' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function startNextServer() {
  return new Promise((resolve, reject) => {
    if (isDev) {
      // In dev mode, assume Next.js dev server is already running
      resolve();
      return;
    }

    // In production, start the Next.js server from the built output
    const nextStart = spawn(
      process.platform === 'win32' ? 'npx.cmd' : 'npx',
      ['next', 'start', '-p', String(PORT)],
      {
        cwd: __dirname,
        stdio: 'pipe',
        env: { ...process.env, NODE_ENV: 'production' },
      }
    );

    nextProcess = nextStart;

    nextStart.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Next.js] ${output}`);
      if (output.includes('Ready') || output.includes('started')) {
        resolve();
      }
    });

    nextStart.stderr.on('data', (data) => {
      console.error(`[Next.js Error] ${data.toString()}`);
    });

    nextStart.on('error', reject);

    // Fallback: resolve after 5 seconds if no "Ready" message
    setTimeout(resolve, 5000);
  });
}

app.whenReady().then(async () => {
  try {
    await startNextServer();
    createWindow();
  } catch (err) {
    console.error('Failed to start Next.js server:', err);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (nextProcess) {
    nextProcess.kill();
  }
  app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
