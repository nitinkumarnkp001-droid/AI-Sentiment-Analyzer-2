let chart;

function analyze() {
    let text = document.getElementById("text").value;

    fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: text })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById("result").innerText = "Sentiment: " + data.sentiment;
            loadStats();
        });
}

function loadStats() {
    fetch("/stats")
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById("chart").getContext("2d");

            if (chart) chart.destroy();

            chart = new Chart(ctx, {
                type: "pie",
                data: {
                    labels: ["Positive", "Negative", "Neutral"],
                    datasets: [{
                        data: [data.positive, data.negative, data.neutral],
                        backgroundColor: ["green", "red", "gray"]
                    }]
                }
            });
        });
}

window.onload = loadStats;