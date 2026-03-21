const steps = [
  {
    text: "Client → Client Hello",
    info: "Client sends supported encryption methods.",
  },
  {
    text: "Server → Server Hello",
    info: "Server selects encryption method.",
  },
  {
    text: "Server → Sending Certificate",
    info: "Server sends SSL certificate.",
  },
  {
    text: "Client → Verifying Certificate",
    info: "Client verifies authenticity.",
  },
  {
    text: "Client → Sending Pre-Master Secret",
    info: "Client generates secret key.",
  },
  {
    text: "Client → Session Key Generated",
    info: "Session key created.",
  },
  {
    text: "Server → Session Key Generated",
    info: "Server derives same key.",
  },
  {
    text: "Secure TLS Session Established",
    info: "Secure communication begins.",
  },
];

let currentStep = 0;
let interval = null;

function startSimulation() {
  resetSimulation();

  const stepList = document.getElementById("steps");
  const packet = document.getElementById("packet");

  // Create step elements
  steps.forEach((step, index) => {
    const li = document.createElement("li");
    li.textContent = step.text;

    // Click to show explanation
    li.addEventListener("click", () => {
      document.getElementById("info").textContent = step.info;
    });

    stepList.appendChild(li);
  });

  const items = document.querySelectorAll("#steps li");

  interval = setInterval(() => {
    if (currentStep >= steps.length) {
      clearInterval(interval);
      return;
    }

    const currentItem = items[currentStep];

    // 🔵 Activate step
    currentItem.classList.add("active");
    document.getElementById("info").textContent = steps[currentStep].info;

    // 🔵 Animate packet
    packet.classList.add("active");

    if (currentStep % 2 === 0) {
      movePacketToServer(packet);
      activateNode("client");
    } else {
      movePacketToClient(packet);
      activateNode("server");
    }

    // ⏳ After animation completes
    setTimeout(() => {
      // Remove active BEFORE marking done
      currentItem.classList.remove("active");
      currentItem.classList.add("done");

      packet.classList.remove("active");
      deactivateNodes();
    }, 1000);

    currentStep++;
  }, 1500);
}

/* ================= RESET ================= */

function resetSimulation() {
  clearInterval(interval);
  interval = null;
  currentStep = 0;

  document.getElementById("steps").innerHTML = "";
  document.getElementById("packet").style.left = "0%";
  document.getElementById("info").textContent =
    "Click 'Start' to begin the TLS handshake simulation.";

  deactivateNodes();
}

/* ================= PACKET MOVEMENT ================= */

function movePacketToServer(packet) {
  packet.style.left = "calc(100% - 28px)";
}

function movePacketToClient(packet) {
  packet.style.left = "0%";
}

/* ================= NODE HIGHLIGHT ================= */

function activateNode(type) {
  document.querySelector(".client").classList.remove("active");
  document.querySelector(".server").classList.remove("active");

  document.querySelector("." + type).classList.add("active");
}

function deactivateNodes() {
  document.querySelector(".client").classList.remove("active");
  document.querySelector(".server").classList.remove("active");
}
