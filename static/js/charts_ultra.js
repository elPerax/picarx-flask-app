// static/js/charts_ultra.js

const ultraCanvas = document.getElementById("ultraChart");

if (ultraCanvas &&
    ultraCanvas.dataset.labels &&
    ultraCanvas.dataset.values) {

    const ultraLabels = JSON.parse(ultraCanvas.dataset.labels);
    const ultraDataValues = JSON.parse(ultraCanvas.dataset.values);

    const ctx = ultraCanvas.getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: ultraLabels,
            datasets: [{
                label: "Distance (cm)",
                data: ultraDataValues,
                tension: 0.25,
                fill: false,
            }],
        },
        options: {
            scales: {
                x: { title: { display: true, text: "Time (UTC)" } },
                y: { title: { display: true, text: "Distance (cm)" } },
            },
        },
    });
}
