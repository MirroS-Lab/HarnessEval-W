const leaderboardRows = [
  {
    sourceOrder: 1,
    model: "Seedance 2.0",
    projectUrl: "https://seed.bytedance.com/en/seedance2_0",
    organization: "ByteDance Seed",
    interface: "Prompt I2V",
    render: 0.6834,
    physicalObs: 0.6306,
    explore: 0.8094,
    intent: 0.8204,
    physicalTrans: 0.6471,
    drift: 0.8002,
    returnScore: 0.7723,
    offscreen: 0.6883,
    avg: 0.7603,
    rank: 1,
  },
  {
    sourceOrder: 2,
    model: "Wan 2.7 I2V",
    projectUrl: "https://wan.video/",
    organization: "Wan / Alibaba Cloud",
    interface: "Prompt I2V",
    render: 0.6292,
    physicalObs: 0.5881,
    explore: 0.7873,
    intent: 0.8364,
    physicalTrans: 0.7106,
    drift: 0.7429,
    returnScore: 0.6854,
    offscreen: 0.6593,
    avg: 0.7501,
    rank: 2,
  },
  {
    sourceOrder: 3,
    model: "Kling 3.0",
    projectUrl: "https://klingai.com/",
    organization: "Kling AI",
    interface: "Prompt I2V",
    render: 0.6467,
    physicalObs: 0.6057,
    explore: 0.7911,
    intent: 0.8257,
    physicalTrans: 0.6322,
    drift: 0.7721,
    returnScore: 0.7545,
    offscreen: 0.6622,
    avg: 0.7445,
    rank: 3,
  },
  {
    sourceOrder: 4,
    model: "MiniMax H3",
    projectUrl: "https://huggingface.co/MiniMaxAI/MiniMax-H3",
    organization: "MiniMax",
    interface: "Prompt I2V",
    render: 0.6669,
    physicalObs: 0.6128,
    explore: 0.7765,
    intent: 0.8167,
    physicalTrans: 0.6686,
    drift: 0.7699,
    returnScore: 0.7232,
    offscreen: 0.6720,
    avg: 0.7433,
    rank: 4,
  },
  {
    sourceOrder: 5,
    model: "Cosmos3-Super",
    projectUrl: "https://www.nvidia.com/en-us/ai/cosmos/",
    organization: "NVIDIA",
    interface: "Prompt I2V",
    render: 0.6671,
    physicalObs: 0.6102,
    explore: 0.7794,
    intent: 0.7510,
    physicalTrans: 0.6017,
    drift: 0.7762,
    returnScore: 0.7059,
    offscreen: 0.6681,
    avg: 0.7191,
    rank: 5,
  },
  {
    sourceOrder: 6,
    model: "HunyuanVideo 1.5",
    projectUrl: "https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5",
    organization: "Tencent Hunyuan",
    interface: "Prompt I2V",
    render: 0.6195,
    physicalObs: 0.5901,
    explore: 0.7762,
    intent: 0.7321,
    physicalTrans: 0.5718,
    drift: 0.7653,
    returnScore: 0.6948,
    offscreen: 0.6320,
    avg: 0.7029,
    rank: 6,
  },
  {
    sourceOrder: 7,
    model: "LingBot World v2",
    projectUrl: "https://technology.robbyant.com/lingbot-world-v2",
    organization: "Robbyant",
    interface: "Camera pose",
    render: 0.6722,
    physicalObs: 0.6329,
    explore: 0.8150,
    intent: 0.5684,
    physicalTrans: 0.4982,
    drift: 0.7953,
    returnScore: 0.7578,
    offscreen: 0.6612,
    avg: 0.6884,
    rank: 7,
  },
  {
    sourceOrder: 8,
    model: "SANA-WM",
    projectUrl: "https://nvlabs.github.io/Sana/WM/",
    organization: "NVIDIA",
    interface: "Native action",
    render: 0.6654,
    physicalObs: 0.6233,
    explore: 0.8252,
    intent: 0.5059,
    physicalTrans: 0.4758,
    drift: 0.7891,
    returnScore: 0.7882,
    offscreen: 0.7231,
    avg: 0.6870,
    rank: 8,
  },
  {
    sourceOrder: 9,
    model: "Wan2.2-TI2V 5B",
    projectUrl: "https://wan.video/",
    organization: "Wan / Alibaba Cloud",
    interface: "Prompt I2V",
    render: 0.6467,
    physicalObs: 0.5856,
    explore: 0.7716,
    intent: 0.6204,
    physicalTrans: 0.5511,
    drift: 0.7605,
    returnScore: 0.6654,
    offscreen: 0.6340,
    avg: 0.6766,
    rank: 9,
  },
  {
    sourceOrder: 10,
    model: "ABot-World",
    projectUrl: "https://amap-cvlab.github.io/ABot-World/",
    organization: "AMAP CV Lab",
    interface: "Native action",
    render: 0.6870,
    physicalObs: 0.6369,
    explore: 0.8282,
    intent: 0.4990,
    physicalTrans: 0.4711,
    drift: 0.7991,
    returnScore: 0.7725,
    offscreen: 0.5992,
    avg: 0.6715,
    rank: 10,
  },
  {
    sourceOrder: 11,
    model: "DreamX-World",
    projectUrl: "https://amap-ml.github.io/DreamX_World/",
    organization: "AMAP-ML / DreamX Team",
    interface: "Native action",
    render: 0.6657,
    physicalObs: 0.6185,
    explore: 0.8196,
    intent: 0.5017,
    physicalTrans: 0.4791,
    drift: 0.7495,
    returnScore: 0.7435,
    offscreen: 0.6686,
    avg: 0.6704,
    rank: 11,
  },
  {
    sourceOrder: 12,
    model: "Lyra 2",
    projectUrl: "https://research.nvidia.com/labs/sil/projects/lyra2/",
    organization: "NVIDIA Spatial Intelligence Lab",
    interface: "Camera pose",
    render: 0.6731,
    physicalObs: 0.6403,
    explore: 0.8069,
    intent: 0.4893,
    physicalTrans: 0.4513,
    drift: 0.7756,
    returnScore: 0.7968,
    offscreen: 0.5639,
    avg: 0.6552,
    rank: 12,
  },
  {
    sourceOrder: 13,
    model: "Fantasy-World",
    projectUrl: "https://fantasy-amap.github.io/fantasy-world/",
    organization: "AMAP, Alibaba Group",
    interface: "Camera pose",
    render: 0.7079,
    physicalObs: 0.6530,
    explore: 0.7592,
    intent: 0.5412,
    physicalTrans: 0.5113,
    drift: 0.7695,
    returnScore: 0.6860,
    offscreen: 0.6242,
    avg: 0.6543,
    rank: 13,
  },
  {
    sourceOrder: 14,
    model: "LTX-2.3",
    projectUrl: "https://ltx.io/model/ltx-2-3",
    organization: "Lightricks / LTX",
    interface: "Prompt I2V",
    render: 0.5532,
    physicalObs: 0.5447,
    explore: 0.7380,
    intent: 0.6045,
    physicalTrans: 0.5334,
    drift: 0.7245,
    returnScore: 0.6333,
    offscreen: 0.5775,
    avg: 0.6463,
    rank: 14,
  },
  {
    sourceOrder: 15,
    model: "HY-WorldPlay 1.5",
    projectUrl: "https://3d-models.hunyuan.tencent.com/world/",
    organization: "Tencent Hunyuan",
    interface: "Camera pose",
    render: 0.6991,
    physicalObs: 0.6518,
    explore: 0.7345,
    intent: 0.4900,
    physicalTrans: 0.4597,
    drift: 0.7646,
    returnScore: 0.7787,
    offscreen: 0.5833,
    avg: 0.6324,
    rank: 15,
  },
  {
    sourceOrder: 16,
    model: "InSpatio-World",
    projectUrl: "https://inspatio.github.io/inspatio-world/",
    organization: "InSpatio Team",
    interface: "Camera pose",
    render: 0.6684,
    physicalObs: 0.6303,
    explore: 0.7072,
    intent: 0.4856,
    physicalTrans: 0.4558,
    drift: 0.7453,
    returnScore: 0.7703,
    offscreen: 0.5403,
    avg: 0.6144,
    rank: 16,
  },
];

const metricGroups = [
  {
    id: "observation",
    label: "Observation Quality",
    metrics: [
      { key: "render", label: "Obs-R", longLabel: "Render observation" },
      { key: "physicalObs", label: "Obs-P", longLabel: "Physical plausibility observation" },
    ],
  },
  {
    id: "transition",
    label: "Transition Correctness",
    metrics: [
      { key: "explore", label: "Explor.", longLabel: "Exploratory transition" },
      { key: "intent", label: "Intent.", longLabel: "Intentional transition" },
      { key: "physicalTrans", label: "Physical", longLabel: "Physical transition" },
    ],
  },
  {
    id: "persistence",
    label: "World Persistence",
    metrics: [
      { key: "drift", label: "Drift", longLabel: "Drift resistance" },
      { key: "returnScore", label: "Return", longLabel: "Return consistency" },
      { key: "offscreen", label: "Offscreen", longLabel: "Offscreen evolution" },
    ],
  },
  {
    id: "summary",
    label: "Summary",
    metrics: [{ key: "avg", label: "Overall", longLabel: "Overall score" }],
  },
];

const allMetrics = metricGroups.flatMap((group) =>
  group.metrics.map((metric) => ({ ...metric, groupId: group.id, groupLabel: group.label })),
);

const state = {
  sortKey: "avg",
  direction: "desc",
  query: "",
  interface: "all",
  groups: new Set(metricGroups.map((group) => group.id)),
  timeline: "release",
};

const metricRanks = Object.fromEntries(
  allMetrics.map((metric) => [
    metric.key,
    new Map(
      leaderboardRows
        .filter((row) => row[metric.key] != null)
        .sort((a, b) => b[metric.key] - a[metric.key] || a.sourceOrder - b.sourceOrder)
        .map((row, index) => [row.sourceOrder, index + 1]),
    ),
  ]),
);

let metricRowObserver = null;

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function refreshIcons(root = document) {
  if (window.lucide) {
    window.lucide.createIcons({ attrs: { "stroke-width": 1.8 }, root });
  }
}

function initials(value) {
  return value
    .replaceAll("-", " ")
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase();
}

function formatScore(value) {
  return value == null ? "--" : (Number(value) * 100).toFixed(1);
}

function activeMetricGroups() {
  const groups = metricGroups.filter((group) => state.groups.has(group.id));
  return groups.length ? groups : metricGroups.filter((group) => group.id === "summary");
}

function activeMetrics() {
  return activeMetricGroups().flatMap((group) => group.metrics);
}

function metricLabel(key) {
  if (key === "rank") return "Rank";
  if (key === "model") return "Model";
  if (key === "interface") return "Interface";
  return allMetrics.find((metric) => metric.key === key)?.label || key;
}

function ensureVisibleSort() {
  if (["rank", "model", "interface"].includes(state.sortKey)) return;
  if (activeMetrics().some((metric) => metric.key === state.sortKey)) return;
  const firstMetric = activeMetrics()[0] || allMetrics.find((metric) => metric.key === "avg");
  state.sortKey = firstMetric.key;
  state.direction = preferredDirection(state.sortKey);
}

function preferredDirection(key) {
  if (key === "rank" || key === "model" || key === "interface") return "asc";
  return "desc";
}

function rowSearchText(row) {
  return [row.model, row.organization, row.interface].join(" ").toLowerCase();
}

function sortValue(row, key) {
  if (key === "model") return row.model;
  if (key === "interface") return row.interface;
  return row[key];
}

function compareRows(a, b) {
  const left = sortValue(a, state.sortKey);
  const right = sortValue(b, state.sortKey);
  const direction = state.direction === "asc" ? 1 : -1;

  if (left == null && right == null) return a.sourceOrder - b.sourceOrder;
  if (left == null) return 1;
  if (right == null) return -1;

  let primary = 0;
  if (typeof left === "string" || typeof right === "string") {
    primary = String(left).localeCompare(String(right));
  } else {
    primary = left - right;
  }

  if (primary === 0) return a.sourceOrder - b.sourceOrder;
  return primary * direction;
}

function filteredRows() {
  const query = state.query.trim().toLowerCase();
  return leaderboardRows
    .filter((row) => state.interface === "all" || row.interface === state.interface)
    .filter((row) => !query || rowSearchText(row).includes(query))
    .sort(compareRows);
}

function sortButton(key, label, title = "") {
  const active = state.sortKey === key;
  const icon = active
    ? ` <i data-sort-indicator data-lucide="arrow-${state.direction === "asc" ? "up" : "down"}" aria-hidden="true"></i>`
    : "";
  return `<button type="button" data-sort-key="${escapeHtml(key)}" title="${escapeHtml(title || `Sort by ${label}`)}">${escapeHtml(label)}${icon}</button>`;
}

function syncMetricRowOffset() {
  const head = document.querySelector("[data-leaderboard-head]");
  const table = document.querySelector(".lb-tbl");
  const firstRow = head?.querySelector("tr.group-row");
  if (!head || !table || !firstRow) return;

  const top = firstRow.getBoundingClientRect().height;
  table.style.setProperty("--metric-row-top", `${top}px`);
}

function setupMetricRowObserver() {
  const head = document.querySelector("[data-leaderboard-head]");
  if (!head) return;

  if (!metricRowObserver && "ResizeObserver" in window) {
    metricRowObserver = new ResizeObserver(() => syncMetricRowOffset());
    metricRowObserver.observe(head);
    window.addEventListener("resize", syncMetricRowOffset, { passive: true });
    document.fonts?.ready?.then(syncMetricRowOffset).catch(() => {});
  }

  syncMetricRowOffset();
}

const timelineStates = {
  release: {
    label: "2026-08-18",
    progress: "0%",
  },
  "coming-soon": {
    label: "Coming Soon",
    progress: "100%",
  },
};

function syncTimeline() {
  const headDate = document.querySelector("[data-timeline-head-date]");
  const progress = document.querySelector("[data-timeline-progress]");
  const buttons = document.querySelectorAll("[data-timeline-choice]");
  const timeline = timelineStates[state.timeline] || timelineStates.release;

  if (headDate) headDate.textContent = timeline.label;
  if (progress) progress.style.width = timeline.progress;

  buttons.forEach((button) => {
    const selected = button.dataset.timelineChoice === state.timeline;
    button.classList.toggle("active", selected);
    button.setAttribute("aria-pressed", String(selected));
  });
}

function setTimeline(choice) {
  if (!timelineStates[choice]) return;
  state.timeline = choice;
  syncTimeline();
}

const submissionTemplate = {
  model_name: "Example Model",
  model_link: "https://example.com/model",
  model_type: "Prompt I2V",
  accessibility: "Unknown",
  team_name: "Example Team",
  contact_email: "contact@example.com",
  scores: {
    obs_r: null,
    obs_p: null,
    exploratory: null,
    intentional: null,
    physical: null,
    drift: null,
    return: null,
    offscreen: null,
    overall: null,
  },
  notes: "Optional verification notes or links.",
};

let selectedSubmissionFile = null;
let selectedSubmissionFileKind = "";

function prettyJson(value) {
  return `${JSON.stringify(value, null, 2)}\n`;
}

function setSubmitStatus(kind, message) {
  const node = document.querySelector("[data-submit-status]");
  if (!node) return;
  node.hidden = false;
  node.classList.toggle("is-ok", kind === "ok");
  node.classList.toggle("is-error", kind === "error");
  node.textContent = message;
}

function fillSubmissionTemplate() {
  const textarea = document.querySelector("[data-submit-json]");
  if (textarea) textarea.value = prettyJson(submissionTemplate);

  document.querySelectorAll("[data-submit-field]").forEach((field) => {
    field.value = "";
  });
}

function parseSubmissionJson() {
  const textarea = document.querySelector("[data-submit-json]");
  const raw = textarea?.value.trim() || "{}";
  const parsed = JSON.parse(raw);
  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error("submission JSON must be an object");
  }
  return parsed;
}

function mergedSubmission() {
  const submission = parseSubmissionJson();
  document.querySelectorAll("[data-submit-field]").forEach((field) => {
    const key = field.dataset.submitField;
    const value = String(field.value || "").trim();
    if (key && value) submission[key] = value;
  });
  return submission;
}

function overallScoreValue(submission) {
  return (
    submission.overall ??
    submission.total_score ??
    submission.total_m_score ??
    submission.scores?.overall ??
    null
  );
}

function validateSubmission(submission) {
  const missing = ["model_name", "model_link", "model_type"].filter(
    (key) => !String(submission[key] ?? "").trim(),
  );
  const overall = overallScoreValue(submission);

  if (missing.length) return `Missing required JSON key(s): ${missing.join(", ")}.`;
  if (overall == null || overall === "") {
    return "Missing overall score. Use overall, total_score, total_m_score, or scores.overall.";
  }

  const numericOverall = Number(overall);
  if (!Number.isFinite(numericOverall) || numericOverall < 0 || numericOverall > 100) {
    return "Overall score must be a number in the 0-100 range.";
  }

  return "";
}

function submissionClientInfo() {
  return {
    page: window.location.pathname,
    submitted_at: new Date().toISOString(),
    user_agent: navigator.userAgent,
  };
}

function submitFieldValues() {
  const values = {};
  document.querySelectorAll("[data-submit-field]").forEach((field) => {
    const key = field.dataset.submitField;
    const value = String(field.value || "").trim();
    if (key && value) values[key] = value;
  });
  return values;
}

function setSubmissionFileName(fileName = "") {
  const node = document.querySelector("[data-submit-file-name]");
  if (!node) return;
  node.textContent = fileName || "No file selected";
}

function setupSubmissionForm() {
  const form = document.querySelector("[data-submit-form]");
  const fileInput = document.querySelector("[data-submit-file]");
  const fileTrigger = document.querySelector("[data-submit-file-trigger]");
  const resetButton = document.querySelector("[data-submit-template]");
  if (!form) return;

  fillSubmissionTemplate();

  fileTrigger?.addEventListener("click", () => {
    fileInput?.click();
  });

  fileInput?.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) {
      selectedSubmissionFile = null;
      selectedSubmissionFileKind = "";
      setSubmissionFileName();
      return;
    }

    selectedSubmissionFile = file;
    selectedSubmissionFileKind = file.name.toLowerCase().endsWith(".zip") ? "zip" : "json";
    setSubmissionFileName(file.name);

    if (selectedSubmissionFileKind === "zip") {
      setSubmitStatus(
        "ok",
        `Loaded ${file.name}. The ZIP should contain leaderboard_submission.json at the root; fill any override fields, then submit.`,
      );
      return;
    }

    try {
      const text = await file.text();
      JSON.parse(text);
      document.querySelector("[data-submit-json]").value = text.trim() ? `${text.trim()}\n` : "";
      setSubmitStatus("ok", `Loaded ${file.name}. Review the JSON, then submit.`);
    } catch (error) {
      selectedSubmissionFile = null;
      selectedSubmissionFileKind = "";
      setSubmissionFileName();
      setSubmitStatus("error", `Could not load JSON: ${error.message}`);
    }
  });

  resetButton?.addEventListener("click", () => {
    selectedSubmissionFile = null;
    selectedSubmissionFileKind = "";
    if (fileInput) fileInput.value = "";
    setSubmissionFileName();
    fillSubmissionTemplate();
    setSubmitStatus("ok", "Template restored. Replace the example values before submitting.");
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const isZipUpload = selectedSubmissionFileKind === "zip" && selectedSubmissionFile;
    let submission = null;

    if (!isZipUpload) {
      try {
        submission = mergedSubmission();
      } catch (error) {
        setSubmitStatus("error", `Invalid JSON: ${error.message}`);
        return;
      }

      const validationError = validateSubmission(submission);
      if (validationError) {
        setSubmitStatus("error", validationError);
        return;
      }
    }

    const submitButton = form.querySelector("button[type='submit']");
    submitButton.disabled = true;
    setSubmitStatus("ok", "Submitting leaderboard results...");

    try {
      let response;
      if (isZipUpload) {
        const formData = new FormData();
        formData.append("submission_file", selectedSubmissionFile, selectedSubmissionFile.name);
        Object.entries(submitFieldValues()).forEach(([key, value]) => formData.append(key, value));
        formData.append("client", JSON.stringify(submissionClientInfo()));
        response = await fetch("/api/submissions", {
          method: "POST",
          body: formData,
        });
      } else {
        response = await fetch("/api/submissions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            submission,
            client: submissionClientInfo(),
          }),
        });
      }
      const result = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(result.error || `Backend returned HTTP ${response.status}`);
      }

      setSubmitStatus(
        "ok",
        `Saved as pending submission ${result.submission_id}. The public leaderboard was not updated.`,
      );
    } catch (error) {
      setSubmitStatus(
        "error",
        `Submission failed: ${error.message}. Start the leaderboard backend server and try again.`,
      );
    } finally {
      submitButton.disabled = false;
    }
  });
}

function renderHeader() {
  const head = document.querySelector("[data-leaderboard-head]");
  if (!head) return;

  const groups = activeMetricGroups();
  head.innerHTML = `
    <tr class="group-row">
      <th rowspan="2" scope="col" class="rank-col">${sortButton("rank", "Rank")}</th>
      <th rowspan="2" scope="col" class="model-col l">${sortButton("model", "Model")}</th>
      <th rowspan="2" scope="col" class="l">${sortButton("interface", "Interface")}</th>
      ${groups
        .map((group) => `<th colspan="${group.metrics.length}" scope="colgroup" class="grp">${escapeHtml(group.label)}</th>`)
        .join("")}
    </tr>
    <tr class="metric-row">
      ${groups
        .flatMap((group) => group.metrics.map((metric, index) => ({ ...metric, first: index === 0 })))
        .map(
          (metric) =>
            `<th scope="col" class="${metric.first ? "grp" : ""}">${sortButton(metric.key, metric.label, `Sort by ${metric.longLabel}`)}</th>`,
        )
        .join("")}
    </tr>
  `;
}

function interfaceClass(value) {
  if (value === "Prompt I2V") return "interface-prompt";
  if (value === "Camera pose") return "interface-camera";
  return "interface-native";
}

function scoreCell(row, metric, firstInGroup = false) {
  const value = row[metric.key];
  const metricRank = metricRanks[metric.key].get(row.sourceOrder);
  const medalRank = metricRank <= 3 ? metricRank : null;
  const medalClass = medalRank ? ["gold", "silver", "bronze"][medalRank - 1] : "";
  const classes = [
    "score-cell",
    firstInGroup ? "grp" : "",
    metric.key === "avg" ? "overall-cell" : "",
    medalClass ? `podium-${medalClass}` : "",
    value == null ? "missing" : "",
  ]
    .filter(Boolean)
    .join(" ");

  if (value == null) return `<td class="${classes}">--</td>`;

  const medal = medalRank
    ? `<span class="score-medal" title="${escapeHtml(metric.longLabel)} rank ${medalRank}">${medalRank}</span>`
    : "";

  return `
    <td class="${classes}">
      <span class="score-entry">
        <span class="score-line">${medal}<span class="score-value">${formatScore(value)}</span></span>
        <span class="score-rank">#${metricRank}</span>
      </span>
    </td>`;
}

function renderRows() {
  const body = document.querySelector("[data-leaderboard-body]");
  const summary = document.querySelector("[data-table-summary]");
  const empty = document.querySelector("[data-empty]");
  if (!body || !summary || !empty) return;

  const rows = filteredRows();
  const groups = activeMetricGroups();
  const metrics = groups.flatMap((group) =>
    group.metrics.map((metric, index) => ({ ...metric, firstInGroup: index === 0 })),
  );

  summary.textContent = `Showing ${rows.length} of ${leaderboardRows.length}. Sorted by ${metricLabel(state.sortKey)} ${state.direction}.`;
  empty.hidden = rows.length > 0;

  body.innerHTML = rows
    .map((row) => {
      return `
        <tr class="row" data-row-id="${row.sourceOrder}">
          <td class="lb-rank">
            <span>${escapeHtml(row.rank)}</span>
          </td>
          <td class="mdl-col l">
            <span class="lb-mdl">
              <span class="model-badge" aria-hidden="true">${escapeHtml(initials(row.model))}</span>
              <a class="model-link" href="${escapeHtml(row.projectUrl)}" target="_blank" rel="noopener noreferrer">
                <span class="model-name">${escapeHtml(row.model)}</span>
              </a>
            </span>
          </td>
          <td class="l interface-cell">
            <span class="interface-pill ${interfaceClass(row.interface)}">${escapeHtml(row.interface)}</span>
          </td>
          ${metrics.map((metric) => scoreCell(row, metric, metric.firstInGroup)).join("")}
        </tr>`;
    })
    .join("");

  refreshIcons(body);
}

function render() {
  renderHeader();
  renderRows();
  refreshIcons(document.querySelector("[data-leaderboard-head]"));
  syncMetricRowOffset();
}

function setTab(name) {
  document.querySelectorAll("[data-tab]").forEach((button) => {
    const active = button.dataset.tab === name;
    button.setAttribute("aria-selected", String(active));
  });
  document.querySelectorAll("[data-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.panel !== name;
  });
}

function syncControls() {
  const search = document.querySelector("[data-search]");
  if (search) search.value = state.query;

  const interfaceSelect = document.querySelector("[data-interface-select]");
  if (interfaceSelect) interfaceSelect.value = state.interface;

  document.querySelectorAll("[data-group]").forEach((button) => {
    button.setAttribute("aria-pressed", String(state.groups.has(button.dataset.group)));
  });

}

function resetState() {
  state.sortKey = "avg";
  state.direction = "desc";
  state.query = "";
  state.interface = "all";
  state.groups = new Set(metricGroups.map((group) => group.id));
  state.timeline = "release";
}

function setupInteractions() {
  document.addEventListener("click", (event) => {
    const timelineTarget = event.target.closest("[data-timeline-choice]");
    if (timelineTarget) {
      setTimeline(timelineTarget.dataset.timelineChoice);
      return;
    }

    const timelineRail = event.target.closest("[data-timeline-rail]");
    if (timelineRail) {
      const rect = timelineRail.getBoundingClientRect();
      const choice = event.clientX >= rect.left + rect.width / 2 ? "coming-soon" : "release";
      setTimeline(choice);
      return;
    }

    const sortTarget = event.target.closest("[data-sort-key]");
    if (sortTarget) {
      const key = sortTarget.dataset.sortKey;
      if (state.sortKey === key) {
        state.direction = state.direction === "desc" ? "asc" : "desc";
      } else {
        state.sortKey = key;
        state.direction = preferredDirection(key);
      }
      render();
      return;
    }

    const tabTarget = event.target.closest("[data-tab]");
    if (tabTarget) {
      setTab(tabTarget.dataset.tab);
      refreshIcons();
      return;
    }

    const groupTarget = event.target.closest("[data-group]");
    if (groupTarget) {
      const id = groupTarget.dataset.group;
      if (state.groups.has(id)) state.groups.delete(id);
      else state.groups.add(id);
      if (!state.groups.size) state.groups.add("summary");
      ensureVisibleSort();
      syncControls();
      render();
      return;
    }

    const actionTarget = event.target.closest("[data-action]");
    if (actionTarget?.dataset.action === "reset") {
      resetState();
      syncControls();
      syncTimeline();
      render();
    }
  });

  document.querySelector("[data-search]")?.addEventListener("input", (event) => {
    state.query = event.target.value;
    renderRows();
  });

  document.querySelector("[data-interface-select]")?.addEventListener("change", (event) => {
    state.interface = event.target.value;
    renderRows();
  });
}

function leader(metricKey) {
  return [...leaderboardRows].sort((a, b) => b[metricKey] - a[metricKey] || a.sourceOrder - b.sourceOrder)[0];
}

function renderFindings() {
  const node = document.querySelector("[data-findings]");
  if (!node) return;

  const bestRender = leader("render");
  const bestObsPhysical = leader("physicalObs");
  const bestExplore = leader("explore");
  const bestIntent = leader("intent");
  const bestPhysical = leader("physicalTrans");
  const bestDrift = leader("drift");
  const bestReturn = leader("returnScore");
  const bestOffscreen = leader("offscreen");

  node.innerHTML = `
    <article class="lb-card">
      <span>Observation leaders</span>
      <strong>${escapeHtml(bestRender.model)}</strong>
      <p>Leads Obs-R at ${formatScore(bestRender.render)}; ${escapeHtml(bestObsPhysical.model)} leads Obs-P at ${formatScore(bestObsPhysical.physicalObs)}.</p>
    </article>
    <article class="lb-card">
      <span>Transition leaders</span>
      <strong>Metric-specific leaders</strong>
      <p>${escapeHtml(bestExplore.model)} leads Exploratory, ${escapeHtml(bestIntent.model)} leads Intentional, and ${escapeHtml(bestPhysical.model)} leads Physical transition.</p>
    </article>
    <article class="lb-card">
      <span>Persistence leaders</span>
      <strong>Metric-specific leaders</strong>
      <p>${escapeHtml(bestDrift.model)} leads Drift, ${escapeHtml(bestReturn.model)} leads Return, and ${escapeHtml(bestOffscreen.model)} leads Offscreen.</p>
    </article>`;
}

document.addEventListener("DOMContentLoaded", () => {
  syncControls();
  syncTimeline();
  setupInteractions();
  setupSubmissionForm();
  renderFindings();
  render();
  setupMetricRowObserver();
  refreshIcons();
});
