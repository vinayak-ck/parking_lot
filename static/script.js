const output = document.getElementById("output");
const vehicleType = document.getElementById("vehicleType");
const vehicleNumber = document.getElementById("vehicleNumber");

// Buttons
document.querySelectorAll(".buttons button").forEach(btn => {
  btn.addEventListener("click", async () => {
    const action = btn.getAttribute("data-action");
    await handleAction(action);
  });
});

// Centralized fetch
async function post(url, data = {}) {
  const body = new URLSearchParams(data);
  const res = await fetch(url, { method: "POST", body });
  const text = await res.text();
  return text;
}

async function handleAction(action) {
  const type = vehicleType.value;
  const number = vehicleNumber.value.trim();

  let url = `/${action}`;
  let payload = { type };

  if (["enter", "exit"].includes(action)) {
    if (!number) {
      show(`⚠ Please enter a vehicle number.`);
      return;
    }
    payload.number = number;
  }

  try {
    const msg = await post(url, payload);
    show(msg);
    await refreshDashboard();
  } catch (e) {
    show("⚠ Backend not responding.");
  }
}

function show(message) {
  output.textContent = message;
}

// ---------- Dashboard ----------
async function refreshDashboard() {
  try {
    const res = await fetch("/state");
    const data = await res.json();

    const { capacity, counts, earnings, parking } = data;

    setStat("cars", counts.car, capacity.car, parking.car);
    setStat("bikes", counts.bike, capacity.bike, parking.bike);
    setStat("rick", counts.rickshaw, capacity.rickshaw, parking.rickshaw);
    setStat("bus", counts.bus, capacity.bus, parking.bus);

    const eCar = earnings.car || 0;
    const eBike = earnings.bike || 0;
    const eRick = earnings.rickshaw || 0;
    const eBus = earnings.bus || 0;
    document.getElementById("earnCar").textContent = eCar;
    document.getElementById("earnBike").textContent = eBike;
    document.getElementById("earnRick").textContent = eRick;
    document.getElementById("earnBus").textContent = eBus;
    document.getElementById("earnTotal").textContent = eCar + eBike + eRick + eBus;
  } catch (e) {
    // ignore for now
  }
}

function setStat(prefix, count, cap, list) {
  const pct = cap ? Math.min(100, Math.round((count / cap) * 100)) : 0;
  document.getElementById(`${prefix}Count`).textContent = `${count}/${cap}`;
  document.getElementById(`${prefix}Bar`).style.width = `${pct}%`;
  const el = document.getElementById(`${prefix}List`);
  el.innerHTML = list.length ? list.map(n => `<div>#${n}</div>`).join("") : "<div>—</div>";
}

// Initial load
refreshDashboard();
