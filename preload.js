const { contextBridge, ipcRenderer } = require('electron');

// Expose APIs to the renderer process
contextBridge.exposeInMainWorld('electronAPI', {
    selectFile: () => ipcRenderer.send('file-selection'),
    onFileSelected: (callback) => ipcRenderer.on('file-selected', (event, filePath) => callback(filePath)),

    recoverData: (filePath) => ipcRenderer.send('recover-data', filePath),
    onRecoveryProgress: (callback) => ipcRenderer.on('recovery-progress', (event, message) => callback(message)),

    cancelRecovery: () => ipcRenderer.send('cancel-recovery'),
});