#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const siteDir = path.resolve(scriptDir, "..");
const repoDir = path.resolve(siteDir, "../..");
const casesDir = path.join(siteDir, "assets/cases");
const controlsDir = path.join(siteDir, "assets/controls");
const gtDir = path.join(siteDir, "assets/gt");
const dataDir = path.join(siteDir, "assets/data");

for (const dir of [casesDir, controlsDir, gtDir, dataDir]) {
  fs.mkdirSync(dir, { recursive: true });
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(repoDir, relativePath), "utf8"));
}

function copyAsset(source, destination) {
  if (!source || !fs.existsSync(source)) return null;
  fs.copyFileSync(source, destination);
  return destination;
}

function pretty(value) {
  return String(value || "")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function compact(text, maxLength = 260) {
  const normalized = String(text || "").replace(/\s+/g, " ").trim();
  if (normalized.length <= maxLength) return normalized;
  return `${normalized.slice(0, maxLength - 3).trim()}...`;
}

function asArray(value) {
  if (value == null || value === "") return [];
  return Array.isArray(value) ? value : [value];
}

function persistenceTaskText(probe, spec) {
  if (spec.prompt) return spec.prompt;
  const preset = pretty(spec.action_preset || "camera trajectory");
  const chunks = Number(spec.num_chunks) || 1;

  if (probe === "drift") {
    return `Run the ${preset} camera-control preset for ${chunks} consecutive rollout chunks. Track whether visual quality, geometry, and registered landmarks remain stable as the route continues.`;
  }
  if (probe === "revisit") {
    return `Follow the ${preset} camera-control route away from the initial view and back. Compare the returned view with the starting state for layout and landmark consistency.`;
  }
  if (probe === "multiview") {
    return `Execute the ${preset} camera-control preset to inspect the same world from multiple directions. Check cross-view identity, geometry, and landmark consistency.`;
  }
  return `Execute the ${preset} camera-control preset and evaluate ${pretty(probe)} persistence in the same world.`;
}

function persistenceExpected(probe, spec) {
  const specific = spec.evolvable_element?.expected_evolution;
  const defaults = {
    drift: [
      `The same world identity and registered landmarks remain traceable through all ${Number(spec.num_chunks) || 1} rollout chunks.`,
      "Rendering quality and scene geometry do not progressively degrade along the route.",
    ],
    revisit: [
      "The returned view recovers the same registered landmarks and relative layout as the initial view.",
      "The route returns to a continuing world rather than a regenerated or reset scene.",
    ],
    offscreen: [
      "The scene continues from its prior state instead of freezing or resetting while out of view.",
    ],
    multiview: [
      "Registered landmarks keep the same identity and relative layout across viewpoints.",
      "Newly revealed regions remain compatible with the same continuous world.",
    ],
  };
  return [specific, ...(defaults[probe] || [])].filter(Boolean).slice(0, 3);
}

function flattenParameters(value, prefix = "") {
  return Object.entries(value || {}).flatMap(([key, item]) => {
    const label = [prefix, pretty(key)].filter(Boolean).join(" / ");
    if (item && typeof item === "object" && !Array.isArray(item)) {
      return flattenParameters(item, label);
    }
    if (Array.isArray(item)) {
      return item.map((entry, index) => `${label} ${index + 1}: ${entry}`);
    }
    return [`${label}: ${item}`];
  });
}

const promptData = readJson("cases/v0/02_world_expansions/image_prompts.json");
const actionData = readJson("cases/v0/04_actions/actions.json");
const persistenceData = readJson("cases/v0/08_persistence/persistence_cases_index.json");
const physicalData = readJson(
  "cases/v0/07_physical_v1/physical_v5_final_model_specs/clean_i2i_inputs/clean_i2i_cases_with_seedream.json",
);

const actionsByCase = new Map(actionData.items.map((item) => [item.case_id, item.actions || []]));
const promptsByCase = new Map(promptData.items.map((item) => [item.id, item]));
const candidatesDir = path.join(repoDir, "cases/v0/03_assets/candidates");
const candidateByCase = new Map();

for (const filename of fs.readdirSync(candidatesDir).sort()) {
  const match = filename.match(/^\d+_((?:nav|sem)_\d+)_/);
  if (!match || filename.includes("old")) continue;
  if (!candidateByCase.has(match[1])) {
    candidateByCase.set(match[1], path.join(candidatesDir, filename));
  }
}

const cases = [];

for (const item of promptData.items) {
  // The July snapshot keeps 10 legacy physical expansions in the 320-action
  // budget, but the browsable physical inventory is the 59-sample sim-GT set.
  if (item.axis !== "semantic" && item.axis !== "navigation") continue;
  const sourceImage = candidateByCase.get(item.id);
  const extension = sourceImage ? path.extname(sourceImage).toLowerCase() : ".jpg";
  const assetName = `${item.id}${extension}`;
  if (sourceImage) copyAsset(sourceImage, path.join(casesDir, assetName));

  const actions = (actionsByCase.get(item.id) || []).map((action) => ({
    id: action.action_id,
    type: action.action_type,
    controls: action.control_sequence || [],
    text: compact(action.action_prompt, 340),
    expected: (action.expected_outcome || []).slice(0, 3),
    anchors: (action.protected_anchors || []).slice(0, 4),
  }));
  const base = item.base_elements || {};

  cases.push({
    id: item.id,
    type: item.axis,
    title: pretty(base.scene || item.id),
    scene: pretty(base.scene),
    style: pretty(base.style),
    perspective: pretty(base.perspective),
    subject: pretty(base.subject),
    image: sourceImage ? `assets/cases/${assetName}` : null,
    prompt: compact(item.image_prompt, 520),
    actions,
    actionCount: actions.length,
  });
}

for (const row of persistenceData.rows) {
  const detailsPath = [
    row.path,
    path.join(repoDir, "cases/v0/08_persistence/cases", `${row.id}.json`),
  ].find((candidate) => candidate && fs.existsSync(candidate));
  if (!detailsPath) throw new Error(`Missing persistence source for ${row.id}.`);

  const details = JSON.parse(fs.readFileSync(detailsPath, "utf8"));
  const sourceCase = row.source_world;
  const sourcePrompt = promptsByCase.get(sourceCase);
  const sourceBase = sourcePrompt?.base_elements || {};
  const sourceImage = candidateByCase.get(sourceCase) || details.initial_image || row.initial_image;
  const extension = sourceImage ? path.extname(sourceImage).toLowerCase() : ".jpg";
  const assetName = `${sourceCase}${extension}`;
  if (sourceImage && !fs.existsSync(path.join(casesDir, assetName))) {
    copyAsset(sourceImage, path.join(casesDir, assetName));
  }

  const action = details.interaction?.action || details.action || {};
  const futures = details.probes?.persistence?.futures || {};
  const future = futures[row.probe] || Object.values(futures)[0];
  if (!future) throw new Error(`Missing persistence future specification for ${row.id}.`);

  const numChunks = Math.max(1, Number(future.num_chunks) || 1);
  const text = action.text || details.instruction || persistenceTaskText(row.probe, future);
  const controls = action.control_sequence
    || action.action_tokens
    || (future.action_preset ? Array(numChunks).fill(future.action_preset) : []);
  const expected = asArray(details.expected_outcome || action.expected_outcome);
  const anchors = asArray(details.anchor_summary || details.stable_anchors || action.protected_anchors);
  cases.push({
    id: row.id,
    type: "persistence",
    title: `${pretty(row.probe)}: ${pretty(sourceBase.scene || sourceCase)}`,
    scene: pretty(sourceBase.scene || sourceCase),
    style: "Persistence Probe",
    perspective: pretty(details.perspective || sourceBase.perspective || "mixed"),
    subject: pretty(row.probe),
    image: sourceImage ? `assets/cases/${assetName}` : null,
    prompt: compact(details.environment_prompt || sourcePrompt?.image_prompt || text, 520),
    actions: [
      {
        id: action.action_id || row.id,
        type: action.type || `persistence_${row.probe}`,
        controls,
        text: compact(text, 340),
        expected: (expected.length ? expected : persistenceExpected(row.probe, future)).slice(0, 3),
        anchors: anchors.slice(0, 4),
      },
    ],
    actionCount: 1,
    legacyProbe: row.probe === "multiview",
  });
}

for (const row of physicalData.rows) {
  const id = `phy_${row.model_id}_${row.sample_id}`;
  const imageName = `${id}.jpg`;
  const controlName = `${id}.mp4`;
  const gtName = `${id}.json`;
  const imageSource = row.seedream_i2i_head_path || row.first_frame_path;
  const imageCopied = copyAsset(imageSource, path.join(casesDir, imageName));
  const controlCopied = copyAsset(row.control_video_path, path.join(controlsDir, controlName));
  const gtCopied = copyAsset(row.gt_path, path.join(gtDir, gtName));
  const gt = row.gt || {};
  const parameters = flattenParameters(gt.parameters || {});
  const lawSource = gt.law_checks || gt.laws || [];
  const laws = Array.isArray(lawSource)
    ? lawSource.map((law) => law.name || law.id || String(law))
    : Object.keys(lawSource);
  const channels = Object.keys(gt.trajectory?.channels || gt.state_channels || {});
  const events = Array.isArray(gt.events)
    ? gt.events.map((event) => event.name || event.id || String(event))
    : Object.keys(gt.events || {});

  cases.push({
    id,
    type: "physical",
    title: pretty(row.model_id),
    scene: pretty(row.model_id),
    style: "Simulator Ground Truth",
    perspective: "Measurement Camera",
    subject: pretty(row.sample_id),
    image: imageCopied ? `assets/cases/${imageName}` : null,
    control: controlCopied ? `assets/controls/${controlName}` : null,
    gt: gtCopied ? `assets/gt/${gtName}` : null,
    prompt: `Oracle-backed physical setup for ${pretty(row.model_id)}. Sample: ${pretty(row.sample_id)}.`,
    parameters,
    laws,
    channels,
    events,
    actions: [],
    actionCount: 0,
  });
}

const typeOrder = { semantic: 0, navigation: 1, physical: 2, persistence: 3 };
cases.sort((a, b) => (typeOrder[a.type] - typeOrder[b.type]) || a.id.localeCompare(b.id));

if (cases.length !== 228) {
  throw new Error(`Expected 228 dataset cards, found ${cases.length}.`);
}

const payload = {
  generatedAt: new Date().toISOString(),
  snapshot: "July 2026",
  counts: {
    all: cases.length,
    semantic: cases.filter((item) => item.type === "semantic").length,
    navigation: cases.filter((item) => item.type === "navigation").length,
    physical: cases.filter((item) => item.type === "physical").length,
    persistence: cases.filter((item) => item.type === "persistence").length,
  },
  cases,
};

fs.writeFileSync(path.join(dataDir, "cases.json"), `${JSON.stringify(payload)}\n`);
console.log(JSON.stringify({ counts: payload.counts, output: "assets/data/cases.json" }));
