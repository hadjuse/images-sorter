// Polyfill TextEncoder/TextDecoder for Jest environment
// This must run before MSW imports
const { TextEncoder, TextDecoder } = require('util');
const { ReadableStream, WritableStream, TransformStream } = require('stream/web');

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;
global.ReadableStream = ReadableStream;
global.WritableStream = WritableStream;
global.TransformStream = TransformStream;

// Polyfill fetch for Node.js environment
global.fetch = require('node-fetch');
global.Request = global.fetch.Request;
global.Response = global.fetch.Response;
global.Headers = global.fetch.Headers;

// Mock BroadcastChannel (not available in Node.js)
global.BroadcastChannel = class BroadcastChannel {
  constructor(name) {
    this.name = name;
  }
  postMessage() {}
  close() {}
  addEventListener() {}
  removeEventListener() {}
};

// Mock MessageChannel (not available in Node.js)
global.MessageChannel = class MessageChannel {
  constructor() {
    this.port1 = { postMessage: () => {}, addEventListener: () => {}, removeEventListener: () => {} };
    this.port2 = { postMessage: () => {}, addEventListener: () => {}, removeEventListener: () => {} };
  }
};


