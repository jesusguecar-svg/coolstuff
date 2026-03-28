const STORAGE_KEY = "phase_dashboard_state_v1";

const model = {
  workstreams: [
    { id: "ws_a", title: "WS-A Content", note: "N3/N4/N7/N8 + TX2/TX3/TX4 completion" },
    { id: "ws_b", title: "WS-B Assessment", note: "CP2/CP4/CP5 + M1-M3 authoring" },
    { id: "ws_c", title: "WS-C QBank", note: "Tag completeness + rationale backlink compliance" },
    { id: "ws_d", title: "WS-D Media", note: "Cluster A-E video/audio completion" },
    { id: "ws_e", title: "WS-E QA/Release", note: "Coverage, weighting, routing, pilot checks" }
  ],
  gates: [
    { id: "g1", title: "G1 Content Completeness", note: "No core [TBD] markers" },
    { id: "g2", title: "G2 Assessment Integrity", note: "Fixed thresholds + remediation logic" },
    { id: "g3", title: "G3 QBank Integrity", note: "100% required tags + rationale schema" },
    { id: "g4", title: "G4 Media Linkage", note: "Each cluster mapped to reinforcement assets" },
    { id: "g5", title: "G5 Pilot Readiness", note: "End-to-end learner flow validated" }
  ],
  tasks: [
    { id: "t1", title: "Fill N3 application/underwriting/delivery blueprint", owner: "Curriculum", source: "phase_IV_plan §7" },
    { id: "t2", title: "Fill N4 retirement blueprint", owner: "Curriculum", source: "phase_IV_plan §7" },
    { id: "t3", title: "Fill TX2 law chapter blueprint", owner: "Curriculum/Law", source: "phase_IV_plan §7" },
    { id: "t4", title: "Upgrade CP2 to CP1/CP3 detail level", owner: "Assessment", source: "phase_IV_plan §7" },
    { id: "t5", title: "Create sprint_2_tag_maps for N3/N4/TX2", owner: "QBank", source: "phase_IV_plan §7" }
  ]
};

const defaultState = Object.fromEntries([
  ...model.workstreams.map(w => [w.id, false]),
  ...model.gates.map(g => [g.id, false]),
  ...model.tasks.map(t => [t.id, false])
]);

let state = loadState();

function loadState() {
  try {
    return { ...defaultState, ...(JSON.parse(localStorage.getItem(STORAGE_KEY)) || {}) };
  } catch {
    return { ...defaultState };
  }
}

function saveState() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function checkbox(id, label, note) {
  const div = document.createElement("div");
  div.className = "card";
  div.innerHTML = `
    <label>
      <input type="checkbox" data-id="${id}" ${state[id] ? "checked" : ""} />
      <span>${label}</span>
    </label>
    <small>${note}</small>
  `;
  return div;
}

function render() {
  const ws = document.getElementById("workstreams");
  const gates = document.getElementById("gates");
  const tasks = document.getElementById("tasksTable");
  ws.innerHTML = "";
  gates.innerHTML = "";
  tasks.innerHTML = "";

  model.workstreams.forEach(w => ws.appendChild(checkbox(w.id, w.title, w.note)));
  model.gates.forEach(g => gates.appendChild(checkbox(g.id, g.title, g.note)));

  model.tasks.forEach(t => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><input type="checkbox" data-id="${t.id}" ${state[t.id] ? "checked" : ""}/></td>
      <td>${t.title}</td>
      <td>${t.owner}</td>
      <td>${t.source}</td>
    `;
    tasks.appendChild(tr);
  });

  const keys = Object.keys(defaultState);
  const done = keys.filter(k => state[k]).length;
  const pct = Math.round((done / keys.length) * 100);
  document.getElementById("progressBar").style.width = `${pct}%`;
  document.getElementById("progressText").textContent = `${pct}%`;
  document.getElementById("metaText").textContent = `${done} of ${keys.length} milestones complete`;

  document.querySelectorAll("input[type='checkbox'][data-id]").forEach(input => {
    input.onchange = e => {
      state[e.target.dataset.id] = e.target.checked;
      saveState();
      render();
    };
  });
}

function exportJson() {
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "phase_dashboard_status.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

document.getElementById("exportBtn").onclick = exportJson;
document.getElementById("resetBtn").onclick = () => {
  if (!confirm("Reset all dashboard statuses?")) return;
  state = { ...defaultState };
  saveState();
  render();
};
document.getElementById("importInput").onchange = async e => {
  const file = e.target.files?.[0];
  if (!file) return;
  try {
    const parsed = JSON.parse(await file.text());
    state = { ...defaultState, ...parsed };
    saveState();
    render();
  } catch {
    alert("Invalid JSON file.");
  }
};

render();
