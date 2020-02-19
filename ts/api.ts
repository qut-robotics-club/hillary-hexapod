import { useState } from "react";

class VisionSystemResult {}

export class Api {
  private ws: WebSocket;
  // private visionResultsCbs: ((result: VisionSystemResult) => void)[];
  private jointStateUpdateCbs: ((update: {
    [jointName: string]: number;
  }) => void)[];

  constructor(ws: WebSocket) {
    this.ws = ws;
    // this.visionResultsCbs = [];
    this.jointStateUpdateCbs = [];
    this.ws.onmessage = event => {
      const results = JSON.parse(event.data);
      this.jointStateUpdateCbs.forEach(cb => cb(results));
      // this.visionResultsCbs.forEach(cb => cb(results));
    };
  }

  setDesiredMotion(x: number, y: number, omega: number) {
    this.ws.send(JSON.stringify({ act: "drive", x, y, omega }));
  }

  getLiveStreamUrl() {
    return _wsUrl("live_stream");
  }

  onJointStateUpdate(cb) {
    this.jointStateUpdateCbs.push(cb);
  }

  onVisionSystemResult(cb) {
    // this.visionResultsCbs.push(cb);
  }

  kick() {
    this.ws.send(JSON.stringify({ act: "kick" }));
  }

  do(command: string) {
    this.ws.send(JSON.stringify({ act: "command", command }));
  }

  setDribbling(enable: boolean) {
    this.ws.send(JSON.stringify({ act: "dribble", enable }));
  }

  setRecording(recording: boolean) {
    this.ws.send(JSON.stringify({ act: "set_recording", recording }));
  }
}

const getMethodNames = (cls: any) =>
  Object.getOwnPropertyNames(cls.prototype).filter(
    prop => typeof cls.prototype[prop] === "function"
  );

export const useApi = ([api, setApi] = useState(null)) =>
  api
    ? api
    : (() => {
        const ws = new WebSocket(_wsUrl("remote_control"));
        ws.onopen = _event => setApi(new Api(ws));
      })();

export const useMockApi = () => {
  const api: any = {};
  getMethodNames(Api).forEach(methodName => {
    api[methodName] = (...args) => {};
    // console.log(`${methodName} called with args ${args}}`) as any;
  });
  return api;
};

const _wsUrl = uri => {
  const url =
    uri.indexOf("ws://") !== -1
      ? new URL(uri)
      : new URL(
          process.env.NODE_ENV === "development"
            ? `ws://localhost:8000/${uri}`
            : uri,
          window.location.href
        );
  url.protocol = url.protocol.replace("http", "ws");
  return url.href;
};
