const baseURL = 'http://127.0.0.1:9800/';
const socket = io.connect(baseURL);

export {
  baseURL,
  socket
};