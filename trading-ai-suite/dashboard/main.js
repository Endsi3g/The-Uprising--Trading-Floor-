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
    let settled = false;

    const settle = (success, error) => {
      if (settled) return;
      settled = true;
      if (success) resolve();
      else reject(error || new Error('Startup failed'));
    };

    if (isDev) {
      settle(true);
      return;
    }

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
        settle(true);
      }
    });

    nextStart.stderr.on('data', (data) => {
      console.error(`[Next.js Error] ${data.toString()}`);
    });

    nextStart.on('error', (err) => settle(false, err));
    nextStart.on('exit', (code) => {
      if (code !== null && code !== 0) settle(false, new Error(`Exit code ${code}`));
    });

    setTimeout(() => settle(false, new Error('Timeout')), 10000);
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
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  if (nextProcess) {
    nextProcess.kill();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
