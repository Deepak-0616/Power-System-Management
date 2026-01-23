const API = "http://127.0.0.1:5000/api";

/* ---------------- UPLOAD ---------------- */

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

/* ---------------- PREDICT ---------------- */

async function generatePrediction() {
  const btn = document.getElementById("generateBtn");
  const result = document.getElementById("predictResult");
  const monthInput = document.getElementById("predictMonth");

  btn.disabled = true;

  try {
    const month = monthInput.value.trim();
    if (!month) {
      result.innerText = "❌ Enter month (e.g., 2025_04)";
      return;
    }

    result.innerText = "⏳ Generating predicted dataset...";

    const res = await fetch(`${API}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ month })
    });

    const data = await res.json();

    if (!res.ok) {
      result.innerText = `❌ ${data.error || "Generation failed"}`;
      return;
    }

    const msg = `✅ Predicted dataset generated for ${month}`;
    result.innerText = msg;

    // ✅ PERSIST RESULT
    sessionStorage.setItem("predictResult", msg);
  }
  catch {
    result.innerText = "❌ Backend not reachable";
  }
  finally {
    btn.disabled = false;
  }
}

/* ---------------- VALIDATE ---------------- */

let chart = null;

async function validateData() {
  const btn = document.getElementById("validateBtn");
  const resultDiv = document.getElementById("validateResult");
  const canvas = document.getElementById("errorChart");

  btn.disabled = true;

  try {
    if (!actualFile.files.length) {
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

    const html = `
      Deviation: <b>${data.error}</b><br>
      Threshold: <b>${data.threshold}</b><br>
      Status:
      <b style="color:${data.attack ? "red" : "lime"}">
        ${data.attack ? "FDI FAILURE" : "FDI GOOD"}
      </b>
    `;

    resultDiv.innerHTML = html;

    // ✅ PERSIST RESULT
    sessionStorage.setItem("validateResult", html);

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
      options: { responsive: false }
    });
  }
  catch {
    resultDiv.innerText = "❌ Validation failed";
  }
  finally {
    btn.disabled = false;
  }
}

/* ---------------- RESTORE UI STATE ---------------- */

document.addEventListener("DOMContentLoaded", () => {
  const pr = document.getElementById("predictResult");
  if (pr && sessionStorage.getItem("predictResult")) {
    pr.innerText = sessionStorage.getItem("predictResult");
  }

  const vr = document.getElementById("validateResult");
  if (vr && sessionStorage.getItem("validateResult")) {
    vr.innerHTML = sessionStorage.getItem("validateResult");
  }
});

/* ---------------- SYSTEM ---------------- */

async function checkSystemState() {
  const res = await fetch(`${API}/state`);
  const data = await res.json();

  if (data.halted) {
    document.querySelectorAll(".global-alert")
      .forEach(e => e.classList.remove("hidden"));
  }
}

async function resetSystem() {
  await fetch(`${API}/reset`, { method: "POST" });
  sessionStorage.clear();
  alert("System reset");
}
