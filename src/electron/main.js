const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('index.html');
    mainWindow.webContents.openDevTools();
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Example IPC communication
ipcMain.on('file-selection', (event) => {
    console.log('File selection triggered');
    // Implement file selection logic here
    event.reply('file-selected', 'ExampleFile.txt');
});

ipcMain.on('recover-data', (event, filePath) => {
    console.log(`Recovering data from: ${filePath}`);
    // Implement data recovery logic here
    event.reply('recovery-progress', 'Recovery completed successfully');
});
