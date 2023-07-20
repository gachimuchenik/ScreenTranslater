const spawn = require('child_process').spawn;
const args = require('process').argv;

const imagePath = args[2];
const childArgv = ['./backend/SingleImage.py', imagePath];
const pythonProcess = spawn('py', childArgv);
