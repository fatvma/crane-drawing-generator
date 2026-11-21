"use strict";

// ---- page elements --------------------------------------------------------
const form = document.getElementById("design-form");
const fields = {
  name: document.getElementById("name"),
  span_m: document.getElementById("span_m"),
  capacity_t: document.getElementById("capacity_t"),
  lifting_height_m: document.getElementById("lifting_height_m"),
  duty_group: document.getElementById("duty_group"),
};
const saveNewButton = document.getElementById("save-new");
const updateButton = document.getElementById("update");
const resetButton = document.getElementById("new-design");
const messageBox = document.getElementById("message");
const listElement = document.getElementById("design-list");
const drawingImage = document.getElementById("drawing");
const downloadLink = document.getElementById("download");

// The reference drawing's crane is the starting point.
const DEFAULTS = {
  name: "My crane",
  span_m: 25,
  capacity_t: 10,
  lifting_height_m: 7.9,
  duty_group: "A5",
};

let currentId = null;     // id of the saved design that is open, or null
let currentSvgUrl = null; // address of the drawing currently shown
let previewTimer = null;

// ---- talking to the server ------------------------------------------------
function describeError(data) {
  // Validation errors (422) come as a list; other errors as one sentence.
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((e) => `${e.loc.slice(1).join(".")}: ${e.msg}`)
      .join("\n");
  }
  return data.detail || "Something went wrong.";
}

async function api(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let data = {};
    try {
      data = await response.json();
    } catch (e) {
      // the body was not JSON; keep the generic message
    }
    throw new Error(describeError(data));
  }
  return response;
}

function jsonRequest(method, body) {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

// ---- reading and writing the form -----------------------------------------
function readCrane() {
  // An empty box is sent as null so the server answers "not a valid number".
  const number = (el) => (el.value.trim() === "" ? null : Number(el.value));
  return {
    span_m: number(fields.span_m),
    capacity_t: number(fields.capacity_t),
    lifting_height_m: number(fields.lifting_height_m),
    duty_group: fields.duty_group.value,
  };
}

function readDesign() {
  return { name: fields.name.value, ...readCrane() };
}

function fillForm(values) {
  for (const key of Object.keys(fields)) {
    fields[key].value = values[key];
  }
}

function showMessage(text, kind) {
  messageBox.textContent = text;
  messageBox.className = kind || "";
  messageBox.hidden = text === "";
}

function updateButtons() {
  updateButton.disabled = currentId === null;
}

// ---- drawing preview ------------------------------------------------------
async function refreshDrawing() {
  try {
    const name = encodeURIComponent(fields.name.value.trim());
    const response = await api(
      `/api/preview/drawing?name=${name}`,
      jsonRequest("POST", readCrane())
    );
    const svgText = await response.text();
    if (currentSvgUrl) URL.revokeObjectURL(currentSvgUrl);
    // Shown through <img>, so scripts inside an SVG could never run.
    currentSvgUrl = URL.createObjectURL(
      new Blob([svgText], { type: "image/svg+xml" })
    );
    drawingImage.src = currentSvgUrl;
    downloadLink.href = currentSvgUrl;
    const fileName = (fields.name.value.trim() || "crane").replace(/[^a-z0-9]+/gi, "-");
    downloadLink.download = `${fileName}.svg`;
    showMessage("", "");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function refreshDrawingSoon() {
  clearTimeout(previewTimer);
  previewTimer = setTimeout(refreshDrawing, 300);
}

// ---- saved designs --------------------------------------------------------
async function refreshList() {
  const response = await api("/api/designs");
  const designs = await response.json();
  listElement.replaceChildren();

  if (designs.length === 0) {
    const empty = document.createElement("li");
    empty.textContent = "No saved designs yet.";
    listElement.appendChild(empty);
    return;
  }
  for (const design of designs) {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    // textContent (not innerHTML) so a design name can never run as code.
    button.textContent =
      `${design.name} (${design.capacity_t} t, ${design.span_m} m)`;
    if (design.id === currentId) button.className = "current";
    button.addEventListener("click", () => openDesign(design.id));
    item.appendChild(button);
    listElement.appendChild(item);
  }
}

async function openDesign(id) {
  try {
    const response = await api(`/api/designs/${id}`);
    const design = await response.json();
    fillForm({ name: design.name, ...design.inputs });
    currentId = design.id;
    updateButtons();
    await refreshList();
    await refreshDrawing();
    showMessage(`Opened "${design.name}". Change it and press Update.`, "ok");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

async function saveDesign(asNew) {
  const isUpdate = !asNew && currentId !== null;
  const url = isUpdate ? `/api/designs/${currentId}` : "/api/designs";
  try {
    const response = await api(url, jsonRequest(isUpdate ? "PUT" : "POST", readDesign()));
    const saved = await response.json();
    currentId = saved.id;
    updateButtons();
    await refreshList();
    await refreshDrawing();
    showMessage(isUpdate ? `Updated "${saved.name}".` : `Saved "${saved.name}".`, "ok");
  } catch (error) {
    showMessage(error.message, "error");
  }
}

function resetForm() {
  fillForm(DEFAULTS);
  currentId = null;
  updateButtons();
  refreshList().catch((error) => showMessage(error.message, "error"));
  refreshDrawing();
}

// ---- start-up -------------------------------------------------------------
async function loadLimits() {
  const response = await api("/api/limits");
  const limits = await response.json();
  for (const key of ["span_m", "capacity_t", "lifting_height_m"]) {
    fields[key].min = limits[key].min;
    fields[key].max = limits[key].max;
    document.getElementById(`hint-${key}`).textContent =
      `Allowed: ${limits[key].min} to ${limits[key].max}`;
  }
  for (const group of limits.duty_groups) {
    fields.duty_group.appendChild(new Option(group, group));
  }
}

form.addEventListener("input", refreshDrawingSoon);
form.addEventListener("submit", (event) => event.preventDefault());
saveNewButton.addEventListener("click", () => saveDesign(true));
updateButton.addEventListener("click", () => saveDesign(false));
resetButton.addEventListener("click", resetForm);

loadLimits()
  .then(resetForm)
  .catch((error) => showMessage(error.message, "error"));