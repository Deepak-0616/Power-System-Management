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
  const res = await fetch(`${API}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ month: predictMonth.value })
  });

  const data = await res.json();
  predictResult.innerText =
    data.status ? "✅ Predicted dataset generated" : "⚠️ Error";
}

async function validateData() {
  const form = new FormData();
  form.append("month", validateMonth.value);
  form.append("file", actualFile.files[0]);

  const res = await fetch(`${API}/validate`, {
    method: "POST",
    body: form
  });

  const data = await res.json();

  if (data.halted) {
    document.getElementById("globalAlert").classList.remove("hidden");
  }

  validateResult.innerText = data.attack
    ? "🚨 FALSE DATA INJECTION CONFIRMED"
    : "✅ NO ERROR DETECTED";
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
