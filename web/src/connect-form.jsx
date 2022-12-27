import { get as hashGet } from "hashquery";
import { el } from "redom";

export class ConnectForm {
    constructor() {
        <form this="el" class="pure-form">
            <fieldset>
                <input this="$server" type="text" id="t_server" class="pure-input-1-2" value={hashGet("server") ?? "http://127.0.0.1:1337"} />
                <button type="submit" class="pure-button pure-button-primary">Connect</button>
            </fieldset>
        </form>;

        this.el.addEventListener("submit", (evt) => {
            evt.preventDefault();
            this.callback?.(this.$server.value);
        });
    }

    update({ callback }) {
        this.callback = callback;
    }
}