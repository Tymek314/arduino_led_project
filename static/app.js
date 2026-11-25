let visualizerSocket = null;
const start_connection = document.getElementById("startconnection")
const startLEDButton = document.getElementById("startled");
const stopLEDButton = document.getElementById("stopled");
const startVisualizerButton = document.getElementById("startvisualizer");
const stopVisualizerButton = document.getElementById("stopvisualizer");
const statusText = document.getElementById("status");

const canvas = document.getElementById("visualizer")
const ctx = canvas.getContext("2d")
let leftBands = [];
let rightBands = [];
let curSelected = [];


start_connection.addEventListener("click", async () => {
    const response = await fetch("/startconnection", {
        method: "POST"
    });
    const result = await response.json();
    document.getElementById("startconnection").style.display = "none";
    document.getElementById("startled").style.display = "inline-block";
});

startLEDButton.addEventListener("click", async () => {
    const response = await fetch("/startled", {
        method: "POST"
    });
    const result = await response.json();
    statusText.textContent = result.status;
    document.getElementById("startled").style.display = "none";
    document.getElementById("stopled").style.display = "inline-block";
});

stopLEDButton.addEventListener("click", async () => {
    const response = await fetch("/stopled", {
        method: "POST"
    });
    const result = await response.json();
    statusText.textContent = result.status;
    document.getElementById("startled").style.display = "inline-block";
    document.getElementById("stopled").style.display = "none";
});


startVisualizerButton.addEventListener("click", async () => {
    await fetch("/startvisualizer", { method: "POST" });
    if (visualizerSocket && visualizerSocket.readyState == WebSocket.OPEN) {
        return;
    }
    visualizerSocket = new WebSocket(`ws://${window.location.host}/ws`)
    visualizerSocket.onopen = () => {
        console.log("Visualizer connected");
    };
    visualizerSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // console.log("Received audio data:", data.cur_selected);
        leftBands = data.left;
        rightBands = data.right;
        curSelected = data.cur_selected;
    };

    visualizerSocket.onclose = () => {
        console.log("Visualizer disconnected");
    };

    visualizerSocket.onerror = (error) => {
        console.log("WebSocket error:", error);
    };
    document.getElementById("startvisualizer").style.display = "none";
    document.getElementById("stopvisualizer").style.display = "inline-block";
});

stopVisualizerButton.addEventListener("click", async () => {
    await fetch("/stopvisualizer", { method: "POST" });
    if(visualizerSocket) {
        visualizerSocket.close()
        visualizerSocket = null;
    }
    document.getElementById("startvisualizer").style.display = "inline-block";
    document.getElementById("stopvisualizer").style.display = "none";
});

async function loadSpeakers() {
    const response = await fetch("/speakers");
    const speakers = await response.json();
    const select = document.getElementById("speaker-select");
    select.innerHTML = "<option value=''>Select a speaker</option>";

    speakers.forEach(speaker => {
        const option = document.createElement("option");
        option.value = speaker.name;
        option.textContent = speaker.name;
        select.appendChild(option);
    });

    document.getElementById("speaker-select").addEventListener("change", updateSpeaker);
}

async function updateSpeaker() {
    const select = document.getElementById("speaker-select");
    const speaker = select.value;
    const response = await fetch("/settings", {method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ speaker: speaker })});
    const result = await response.json();
    console.log(result);
}


function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}


function drawBands(bands, x, y, width, height, bassSel, curMax) {
    const count = bands.length;
    if (count === 0) return;
    const gap = 4;
    const barWidth = (width - gap * (count - 1)) / count;
    // Adjust this to match your actual magnitude range
    const maxMagnitude = 200.0;
    bands.forEach((magnitude, i) => {
        const normalized = Math.min(magnitude / maxMagnitude, 1);
        const barHeight = normalized * height;
        const barX = x + i * (barWidth + gap);
        const barY = y + height - barHeight;
        if (i == bassSel) {
            ctx.fillStyle = "#e61b00";
        }
        else if (i == curMax){
            ctx.fillStyle = "#00d7e6"
        }
        else {
            ctx.fillStyle = "#2af06c";
        }
        ctx.fillRect(
            barX,
            barY,
            barWidth,
            barHeight
        );
    });
}


function drawVisualizer() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    ctx.clearRect(0, 0, width, height);
    const halfHeight = height / 2;
    // Left channel - top half
    drawBands(leftBands, 10, 10, width - 20, halfHeight - 10, curSelected[0], curSelected[2] +6);
    // Right channel - bottom half
    drawBands(rightBands, 10, halfHeight + 10, width - 20, halfHeight - 10, curSelected[1], curSelected[3] +6);
    requestAnimationFrame(drawVisualizer);
}


resizeCanvas();
drawVisualizer();

window.addEventListener("resize", resizeCanvas);
loadSpeakers();
