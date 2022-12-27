import { Name } from "@ndn/packet";
import mitt from "mitt";

export class Server {
    constructor(uri = "http://127.0.0.1:1337") {
        this.uri = uri;
    }

    async listFiles() {
        const response = await fetch(`${this.uri}/files/`);
        return response.json();
    }

    readJSON(filename) {
        return this.openWebSocket(`/ws/?filename=${encodeURIComponent(filename)}`);
    }

    openWebSocket(path) {
        const emitter = mitt();
        const ws = new WebSocket(`${this.uri.replace(/^http/, "ws")}${path}`);
        ws.addEventListener("message", (ev) => {
            const j = JSON.parse(ev.data);
            j.ts = new Date(j.ts / 1e6); // convert from nanoseconds to milliseconds
            j.name = new Name(j.name);
            emitter.emit("packet", j);
        });
        ws.addEventListener("close", () => {
            emitter.emit("close");
        });
        emitter.close = () => {
            ws.close();
        };
        return emitter;
    }
}