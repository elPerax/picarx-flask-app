// static/js/charts_gray.js

const grayCanvas = document.getElementById("grayChart");

if (grayCanvas &&
    grayCanvas.dataset.labels &&
    grayCanvas.dataset.left &&
    grayCanvas.dataset.mid &&
    grayCanvas.dataset.right) {

    const grayLabels   = JSON.parse(grayCanvas.dataset.labels);
    const leftVals     = JSON.parse(grayCanvas.dataset.left);
    const midVals      = JSON.parse(grayCanvas.dataset.mid);
    const rightVals    = JSON.parse(grayCanvas.dataset.right);

    const ctx = grayCanvas.getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: grayLabels,
            datasets: [
                { label: "Left",  data: leftVals,  tension: 0.25, fill: false },
                { label: "Mid",   data: midVals,   tension: 0.25, fill: false },
                { label: "Right", data: rightVals, tension: 0.25, fill: false },
            ],
        },
        options: {
            scales: {
                x: { title: { display: true, text: "Time (UTC)" } },
                y: { title: { display: true, text: "Raw grayscale value" } },
            },
        },
    });
}
