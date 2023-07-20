const spawn = require('child_process').spawn;

const childArgv = ['./backend/ClipboardTranslate.py'];
const pythonProcess = spawn('py', childArgv);
