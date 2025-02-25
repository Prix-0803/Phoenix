const { ipcRenderer } = require('electron');

// File selection logic
const selectFileButton = document.getElementById('select-file');
const recoverDataButton = document.getElementById('recover-data');
const cancelRecoveryButton = document.getElementById('cancel-recovery');
const progressText = document.getElementById('progress');

let selectedFilePath = '';
let recovering = false;

selectFileButton.addEventListener('click', () => {
    ipcRenderer.send('file-selection');
});

ipcRenderer.on('file-selected', (event, filePath) => {
    if (filePath) {
        selectedFilePath = filePath;
        progressText.textContent = `Selected File: ${filePath}`;
    }
});

recoverDataButton.addEventListener('click', () => {
    if (selectedFilePath && !recovering) {
        recovering = true;
        document.getElementById('modal').classList.add('show');
        progressText.textContent = 'Recovering data...';
        ipcRenderer.send('recover-data', selectedFilePath);
    }
});

ipcRenderer.on('recovery-progress', (event, message) => {
    recovering = false;
    document.getElementById('modal').classList.remove('show');
    progressText.textContent = message;
});

cancelRecoveryButton.addEventListener('click', () => {
    recovering = false;
    document.getElementById('modal').classList.remove('show');
    progressText.textContent = 'Recovery canceled';
});
