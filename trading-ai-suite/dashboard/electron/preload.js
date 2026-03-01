// Trading AI Suite — Electron Preload Script
// Exposes safe platform info to the renderer process.

const { contextBridge } = require("electron");

contextBridge.exposeInMainWorld("electronAPI", {
  platform: process.platform,
  isElectron: true,
});
