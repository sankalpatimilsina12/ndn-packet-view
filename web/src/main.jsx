import "purecss";
import "./style.css";

import { el, mount, router } from "redom";

import { ConnectForm } from "./connect-form.jsx";
import { Plots } from "./plots.jsx";
import { Server } from "./server.js";
import { StartForm } from "./start-form.jsx";

let server;

const app = router(".app", {
    connect: ConnectForm,
    start: StartForm,
    plots: Plots,
});
mount(document.body, (
    <div>
        {app}
    </div>
));

app.update("connect", {
    callback: selectServer,
});

async function selectServer(serverUri) {
    if (serverUri) {
        server = new Server(serverUri);
    }
    const [files] = await Promise.all([
        server.listFiles(),
    ]);

    app.update("start", {
        files,
        callback: startPlots,
    });
}

function startPlots({ file, prefixlen, suffixlen }) {
    const stream = server.readJSON(file);
    app.update("plots", {
        stream,
        prefixlen,
        suffixlen,
        exit: () => selectServer(undefined),
    });
}