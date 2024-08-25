import {socket, baseURL} from "../../static/socket.js";

// socket.emit('get_highest_rated_candidate')
socket.on('connect', () => console.log('Hello socket working'));

