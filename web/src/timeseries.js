import Chart from "chart.js";
import { el } from "redom";

export class TimeSeries {
    constructor() {
        this.data = [];
        this.clear();
        this.el = el("canvas");
    }

    onmount() {
        this.chart = new Chart(this.el, {
            type: "line",
            data: {
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
                scales: {
                    xAxes: [{
                        type: "time",
                        display: true,
                        time: {
                            displayFormats: {
                                second: "HH:mm:ss",
                            },
                            unit: "second",
                        },
                    }],
                },
                plugins: {
                    datalabels: {
                        display: false,
                    },
                },
            },
        });
    }

    clear() {
        this.second = 0;
        this.count = 0;
        this.data.splice(0, Infinity);
        this.chart?.update();
    }

    push({ ts }) {
        const sec = (ts.getTime() / 1000).toFixed(0);
        if (this.second === 0) {
            this.second = sec;
        }

        let needUpdate = false;
        while (this.second < sec) {
            this.data.push({
                t: new Date(this.second * 1000),
                y: this.count,
            });
            ++this.second;
            this.count = 0;
            needUpdate = true;
        }
        if (needUpdate) {
            while (this.data.length > 300) {
                this.data.shift();
            }
            this.chart?.update();
        }

        ++this.count;
    }
}