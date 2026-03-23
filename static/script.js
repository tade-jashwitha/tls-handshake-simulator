let steps = [];
let currentStep = 0;
let interval = null;

function setStatus(text, colorClasses) {
  const badge = document.getElementById("status-badge");
  badge.textContent = text;
  badge.className = `px-3 py-1 text-xs font-medium rounded-full border transition-all duration-500 ${colorClasses}`;
}

function setProgress(pct) {
  document.getElementById("progress-bar").style.width = pct + "%";
}

function checkAutoScroll() {
  const toggle = document.getElementById("auto-scroll-toggle");
  if (toggle && toggle.checked) {
    const rsaPanel = document.getElementById("rsa-panel");
    if (!rsaPanel.classList.contains("rsa-panel-hidden")) {
      rsaPanel.scrollIntoView({ behavior: "smooth", block: "end" });
    } else {
      document
        .getElementById("details-section")
        .scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }
}

function setDirection(text) {
  const label = document.getElementById("direction-label");
  label.textContent = text;
  label.style.opacity = text ? "1" : "0";
}

async function startSimulation() {
  resetSimulation();
  setStatus(
    "Connecting…",
    "text-amber-400 border-amber-500/30 bg-amber-900/10 shadow-[0_0_10px_rgba(251,191,36,0.2)]",
  );

  try {
    const response = await fetch("/simulate");
    steps = await response.json();
  } catch (error) {
    console.error("Simulation failed to fetch", error);
    document.getElementById("info").textContent =
      "Could not reach the backend. Is Flask running?";
    setStatus(
      "Error",
      "text-red-400 border-red-500/30 bg-red-900/10 shadow-[0_0_10px_rgba(248,113,113,0.2)]",
    );
    return;
  }

  setStatus(
    "Running",
    "text-cyan-400 border-cyan-500/30 bg-cyan-900/10 animate-pulse shadow-[0_0_10px_rgba(34,211,238,0.3)]",
  );

  const stepList = document.getElementById("steps");
  const packet = document.getElementById("packet");

  steps.forEach((step, index) => {
    const li = document.createElement("li");
    const numSpan = document.createElement("span");
    numSpan.className = "step-num";
    numSpan.textContent = index + 1;
    const textSpan = document.createElement("span");
    textSpan.textContent = step.text;

    li.appendChild(numSpan);
    li.appendChild(textSpan);
    li.className = "step-item";

    li.addEventListener("click", () => {
      document.getElementById("info").textContent = step.info;
      updateRsaPanel(step.rsa_details);
      setTimeout(() => checkAutoScroll(), 100);
    });

    stepList.appendChild(li);
  });

  const items = document.querySelectorAll("#steps li");

  interval = setInterval(() => {
    if (currentStep >= steps.length) {
      clearInterval(interval);
      setStatus(
        "Secure ✓",
        "text-emerald-400 border-emerald-500/30 bg-emerald-900/10 shadow-[0_0_15px_rgba(16,185,129,0.3)]",
      );
      setProgress(100);
      setDirection("");
      return;
    }

    const currentItem = items[currentStep];
    const currentData = steps[currentStep];

    setProgress(Math.round(((currentStep + 1) / steps.length) * 100));
    checkAutoScroll();

    currentItem.classList.add("step-active");
    document.getElementById("info").textContent = currentData.info;
    updateRsaPanel(currentData.rsa_details);

    packet.classList.add("visible");
    const wire = document.querySelector(".wire-active-bg");
    const isClientToServer = currentData.text.startsWith("Client");

    if (isClientToServer) {
      setDirection("Client → Server");
      movePacketToServer(packet);
      activateNode("client-node", "active-client");
      packet.classList.remove("packet-fuchsia");
      packet.classList.add("packet-cyan");
      wire.classList.remove("wire-fill-backward");
      wire.classList.add("wire-fill-forward");
      document.getElementById("arrow-right").style.color = "#22d3ee";
      document.getElementById("arrow-left").style.color = "#334155";
    } else {
      setDirection("Server → Client");
      movePacketToClient(packet);
      activateNode("server-node", "active-server");
      packet.classList.remove("packet-cyan");
      packet.classList.add("packet-fuchsia");
      wire.classList.remove("wire-fill-forward");
      wire.classList.add("wire-fill-backward");
      document.getElementById("arrow-left").style.color = "#d946ef";
      document.getElementById("arrow-right").style.color = "#334155";
    }

    setTimeout(() => {
      currentItem.classList.remove("step-active");
      currentItem.classList.add("step-done");
      const num = currentItem.querySelector(".step-num");
      num.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>`;
      packet.classList.remove("visible");
      wire.classList.remove("wire-fill-forward", "wire-fill-backward");
      document.getElementById("arrow-right").style.color = "#334155";
      document.getElementById("arrow-left").style.color = "#334155";
      deactivateNodes();
      setDirection("");
      checkAutoScroll();
    }, 1100);

    currentStep++;
  }, 1600);
}

function resetSimulation() {
  clearInterval(interval);
  interval = null;
  currentStep = 0;

  document.getElementById("steps").innerHTML = "";
  const packet = document.getElementById("packet");
  packet.style.left = "0%";
  packet.classList.remove("visible", "packet-cyan", "packet-fuchsia");

  const wire = document.querySelector(".wire-active-bg");
  if (wire) wire.classList.remove("wire-fill-forward", "wire-fill-backward");

  document.getElementById("info").textContent =
    'Click "Run Handshake" to observe the TLS handshake sequence step by step.';

  setStatus("Idle", "text-gray-400 border-white/10 bg-surface");
  setProgress(0);
  setDirection("");

  const rsaPanel = document.getElementById("rsa-panel");
  rsaPanel.classList.remove("rsa-panel-visible");
  rsaPanel.classList.add("rsa-panel-hidden");

  document.getElementById("arrow-left").style.color = "#334155";
  document.getElementById("arrow-right").style.color = "#334155";

  deactivateNodes();
  if (document.getElementById("auto-scroll-toggle").checked) {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function updateRsaPanel(details) {
  const panel = document.getElementById("rsa-panel");
  const container = document.getElementById("rsa-data-container");

  if (!details) {
    panel.classList.remove("rsa-panel-visible");
    panel.classList.add("rsa-panel-hidden");
    return;
  }

  panel.classList.remove("rsa-panel-hidden");
  panel.classList.add("rsa-panel-visible");
  container.innerHTML = "";

  for (const [key, value] of Object.entries(details)) {
    const card = document.createElement("div");
    card.className = "crypto-card";
    const label = document.createElement("div");
    label.className = "crypto-label";
    label.textContent = key;
    const val = document.createElement("div");
    val.className = "crypto-value";
    val.textContent = value;
    card.appendChild(label);
    card.appendChild(val);
    container.appendChild(card);
  }
}

function movePacketToServer(packet) {
  packet.style.left = "calc(100% - 10px)";
}
function movePacketToClient(packet) {
  packet.style.left = "0%";
}

function activateNode(id, className) {
  deactivateNodes();
  document.getElementById(id).classList.add(className);
}

function deactivateNodes() {
  document
    .getElementById("client-node")
    ?.classList.remove("active-client", "active-server");
  document
    .getElementById("server-node")
    ?.classList.remove("active-client", "active-server");
}
