import { useState } from "react";

class VisionSystemResult {}

export class API {
  ws: WebSocket;
  results_cbs: ((VisionSystemResult) => void)[];

  constructor(ws: WebSocket) {
    this.ws = ws;
    this.results_cbs = [];
    this.ws.onmessage = event => {
      const results = JSON.parse(event.data);
      this.results_cbs.forEach(cb => cb(results));
    };
  }

  async setDesiredMotion(x, y, omega) {
    this.ws.send(JSON.stringify({ act: "drive", x, y, omega }));
  }

  getLiveStreamUrl = () => _wsUrl("live_stream");

  onVisionSystemResult(cb) {
    this.results_cbs.push(cb);
  }

  kick = () => {
    console.log("kick called");
    this.ws.send(JSON.stringify({ act: "kick" }));
  };

  setDribbling = enable => {
    console.log("setting dribble via api", enable);
    this.ws.send(JSON.stringify({ act: "dribble", enable }));
  };

  setRecording = recording => {
    this.ws.send(JSON.stringify({ act: "set_recording", recording }));
  };
}

export const useApi = ([api, setApi] = useState(null)) =>
  api
    ? api
    : (() => {
        const ws = new WebSocket(_wsUrl("remote_control"));
        ws.onopen = _event => setApi(new API(ws));
      })();

const _wsUrl = uri => {
  const url =
    uri.indexOf("ws://") !== -1
      ? new URL(uri)
      : new URL(`/${uri}`, window.location.href);
  url.protocol = url.protocol.replace("http", "ws");
  return url.href;
};
