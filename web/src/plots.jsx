import { AltUri } from "@ndn/naming-convention2";
import { el } from "redom";

import { TimeSeries } from "./timeseries.js"; // eslint-disable-line no-unused-vars
import { Tree } from "./tree.js"; // eslint-disable-line no-unused-vars

export class Plots {
    constructor() {
        <div this="el" class="pure-g">
            <div class="pure-u-1-2">
                <TimeSeries this="$timeseries" />
            </div>
            <div class="pure-u-1-2">
                <Tree this="$tree" />
            </div>
            <div class="pure-u-1">
                <pre this="$recents">recent packets</pre>
            </div>
            <div class="pure-u-1">
                <button this="$stop" class="pure-button">Stop</button>
                <button this="$exit" class="pure-button" disabled>Exit</button>
            </div>
        </div>;

        this.recents = [];
        this.stopped = true;
        this.$stop.addEventListener("click", (evt) => {
            evt.preventDefault();
            this.stop();
            this.$stop.disabled = true;
            this.$exit.disabled = false;
        });
        this.$exit.addEventListener("click", (evt) => {
            evt.preventDefault();
            this.exit?.();
        });
    }

    update({ stream, prefixlen, suffixlen, exit }) {
        this.stop();
        this.stream = stream;
        this.$tree.update({ prefixlen, suffixlen });
        this.stream?.on("packet", (packet) => this.push(packet));
        this.exit = exit;
    }

    stop() {
        this.stream?.close();
    }

    push(packet) {
        this.$timeseries.push(packet);
        this.$tree.push(packet);

        this.recents.push(AltUri.ofName(packet.name));
        while (this.recents.length > 10) {
            this.recents.shift();
        }
        this.$recents.textContent = this.recents.join("\n");
    }
}