// Preload script for Electron
// This runs in a sandboxed context before the renderer process loads

const { contextBridge } = require('electron');

// Expose protected methods that allow the renderer process to use
// specific Electron APIs without giving access to the entire Node.js environment
contextBridge.exposeInMainWorld('electronAPI', {
  // You can add custom APIs here if needed
  platform: process.platform,
  versions: {
    node: process.versions.node,
    chrome: process.versions.chrome,
    electron: process.versions.electron,
  },
});
