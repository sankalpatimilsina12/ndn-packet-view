import "chartjs-chart-graph";
import "chartjs-plugin-datalabels";

import { AltUri } from "@ndn/naming-convention2";
import { toHex } from "@ndn/tlv";
import Chart from "chart.js";
import { el } from "redom";

export class Tree {
    constructor() {
        this.labels = ["/"];
        this.data = [{ name: "/" }];
        this.map = new Map();
        this.clear();

        this.el = el("canvas");
    }

    onmount() {
        this.chart = new Chart(this.el, {
            type: "tree",
            data: {
                labels: this.labels,
                datasets: [
                    {
                        data: this.data,
                    },
                ],
            },
            options: {
                aspectRatio: 1.5,
                legend: {
                    display: false,
                },
                tree: {
                    orientation: "vertical",
                },
                plugins: {
                    datalabels: {
                        formatter: (v) => v.name,
                    },
                },
            },
        });
    }

    clear() {
        this.labels.splice(1, Infinity);
        this.data.splice(1, Infinity);
        this.map.clear();
        this.map.set("", 0);
        this.chart?.update();
    }

    update({ prefixlen, suffixlen }) {
        this.prefixlen = prefixlen;
        this.suffixlen = suffixlen;
    }

    push({ name }) {
        if (++this.count === 1) {
            this.dataset.data.pop();
        }

        let needUpdate = false;
        let parent = 0;
        for (let i = this.prefixlen; i <= name.length - this.suffixlen; ++i) {
            const prefix = name.getPrefix(i);
            const prefixHex = toHex(prefix.value);
            let index = this.map.get(prefixHex);
            if (typeof index === "undefined") {
                index = this.labels.length;
                const record = { parent };
                if (i === this.prefixlen) {
                    record.name = AltUri.ofName(prefix);
                } else {
                    record.name = AltUri.ofComponent(name.at(i - 1));
                }
                this.labels.push(AltUri.ofName(prefix));
                this.data.push(record);
                this.map.set(prefixHex, index);
                needUpdate = true;
            }
            parent = index;
        }

        if (needUpdate) {
            this.chart?.update();
        }
    }
}