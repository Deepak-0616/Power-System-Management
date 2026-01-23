const API = "http://127.0.0.1:5000/api";

async function uploadDataset() {
  const form = new FormData();
  form.append("month", month.value);
  form.append("file", file.files[0]);

  await fetch(`${API}/upload`, { method: "POST", body: form });
  loadDatasets();
}

async function loadDatasets() {
  const res = await fetch(`${API}/list`);
  const data = await res.json();
  datasetList.innerHTML = data.map(m => `<li>${m}</li>`).join("");
}

async function generatePrediction() {
  const month = predictMonth.value.trim();

  if (!month) {
    predictResult.innerText = "❌ Please enter month (e.g., 2022_05)";
    return;
  }

  predictResult.innerText = "⏳ Generating predicted dataset...";

  let res;
  try {
    res = await fetch(`${API}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ month })
    });
  } catch (e) {
    predictResult.innerText = "❌ Backend not reachable";
    return;
  }

  let data;
  try {
    data = await res.json();
  } catch {
    predictResult.innerText = "❌ Invalid response from backend";
    return;
  }

  if (!res.ok) {
    predictResult.innerText = `❌ ${data.error || "Generation failed"}`;
    return;
  }

  // ✅ THIS LINE WAS NEVER REACHED BEFORE
  predictResult.innerText = `✅ Predicted dataset generated for ${month}`;
}

let chart = null;

async function validateData() {
  const resultDiv = document.getElementById("validateResult");
  const canvas = document.getElementById("errorChart");

  if (typeof Chart === "undefined") {
    resultDiv.innerText = "❌ Chart.js not loaded";
    return;
  }

  if (!actualFile.files || actualFile.files.length === 0) {
    resultDiv.innerText = "❌ Please choose actual CSV file";
    return;
  }

  resultDiv.innerText = "⏳ Validating and generating chart...";

  const form = new FormData();
  form.append("month", validateMonth.value.trim());
  form.append("file", actualFile.files[0]);

  const res = await fetch(`${API}/validate`, {
    method: "POST",
    body: form
  });

  const data = await res.json();

  if (!res.ok) {
    resultDiv.innerText = `❌ ${data.error}`;
    return;
  }

  resultDiv.innerHTML = `
    Deviation: <b>${data.error}</b><br>
    Threshold: <b>${data.threshold}</b><br>
    Status:
    <b style="color:${data.attack ? "red" : "lime"}">
      ${data.attack ? "FDI FAILURE" : "FDI GOOD"}
    </b>
  `;

  const ctx = canvas.getContext("2d");

  if (chart) chart.destroy();

  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Deviation", "Threshold"],
      datasets: [{
        label: "FDI Validation",
        data: [data.error, data.threshold],
        backgroundColor: ["#ff4d4d", "#4dff88"]
      }]
    },
    options: {
      responsive: false
    }
  });
}

async function checkSystemState() {
  const res = await fetch(`${API}/state`);
  const data = await res.json();

  if (data.halted) {
    document.querySelectorAll(".global-alert")
      .forEach(e => e.classList.remove("hidden"));
  }
}

window.onload = () => {
  if (typeof loadDatasets === "function") loadDatasets();
  checkSystemState();
};
