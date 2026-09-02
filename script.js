const heroImageSets = [
  [
    { caseId: "sem_0001", src: "assets/hero/set-a-1-street-market.webp" },
    { caseId: "nav_0002", src: "assets/hero/set-a-2-mountain-trail.webp" },
    {
      caseId: "phy_prism_dispersion_fan_single_disperse_clean",
      src: "assets/hero/set-a-3-prism-dispersion.webp",
    },
    { caseId: "per_nav_0007_revisit", src: "assets/hero/set-a-4-museum-revisit.webp" },
    { caseId: "sem_0036", src: "assets/hero/set-a-5-river-waterfall.webp" },
    { caseId: "nav_0017", src: "assets/hero/set-a-6-orchard-path.webp" },
  ],
  [
    { caseId: "nav_0025", src: "assets/hero/set-b-1-subway-station.webp" },
    { caseId: "sem_0015", src: "assets/hero/set-b-2-temple-interior.webp" },
    { caseId: "per_nav_0008_offscreen", src: "assets/hero/set-b-3-public-square-offscreen.webp" },
    {
      caseId: "phy_newton_cradle_transfer_single_release_clean",
      src: "assets/hero/set-b-4-newton-cradle.webp",
    },
    { caseId: "nav_0031", src: "assets/hero/set-b-5-airport-tarmac.webp" },
    { caseId: "sem_0066", src: "assets/hero/set-b-6-desert-ruins.webp" },
  ],
  [
    {
      caseId: "phy_orbit_inverse_square_single_orbit_clean",
      src: "assets/hero/set-c-1-orbit.webp",
    },
    { caseId: "per_nav_0012_offscreen", src: "assets/hero/set-c-2-shopping-mall-offscreen.webp" },
    { caseId: "sem_0030", src: "assets/hero/set-c-3-city-rooftop.webp" },
    { caseId: "nav_0043", src: "assets/hero/set-c-4-botanical-garden.webp" },
    { caseId: "sem_0084", src: "assets/hero/set-c-5-farmland.webp" },
    { caseId: "nav_0035", src: "assets/hero/set-c-6-snowy-village.webp" },
  ],
];

const leaderboardRows = [
  {
    sourceOrder: 1,
    model: "Seedance 2.0",
    projectUrl: "https://seed.bytedance.com/en/seedance2_0",
    organization: "ByteDance Seed",
    organizationIcon: "assets/institutions/bytedance-seed.png",
    interface: "Prompt I2V",
    render: 0.836,
    physicalObs: 0.618,
    explore: 0.802,
    intent: 0.818,
    physicalTrans: 0.635,
    drift: 0.798,
    returnScore: 0.768,
    offscreen: 0.689,
    avg: 0.755,
    rank: 1,
  },
  {
    sourceOrder: 2,
    model: "Wan 2.7",
    projectUrl: "https://wan.video/",
    organization: "Wan / Alibaba Cloud",
    organizationIcon: "assets/institutions/wan-video.png",
    interface: "Prompt I2V",
    render: 0.809,
    physicalObs: 0.588,
    explore: 0.787,
    intent: 0.836,
    physicalTrans: 0.711,
    drift: 0.743,
    returnScore: 0.685,
    offscreen: 0.659,
    avg: 0.750,
    rank: 2,
  },
  {
    sourceOrder: 3,
    model: "Kling 3.0",
    projectUrl: "https://klingai.com/",
    organization: "Kling AI",
    organizationIcon: "assets/institutions/kling-ai.png",
    interface: "Prompt I2V",
    render: 0.821,
    physicalObs: 0.606,
    explore: 0.791,
    intent: 0.826,
    physicalTrans: 0.632,
    drift: 0.772,
    returnScore: 0.754,
    offscreen: 0.662,
    avg: 0.744,
    rank: 3,
  },
  {
    sourceOrder: 4,
    model: "MiniMax H3",
    projectUrl: "https://www.minimax.io/",
    organization: "MiniMax",
    organizationIcon: "assets/institutions/minimax.png",
    interface: "Prompt I2V",
    render: 0.815,
    physicalObs: 0.613,
    explore: 0.777,
    intent: 0.817,
    physicalTrans: 0.669,
    drift: 0.770,
    returnScore: 0.723,
    offscreen: 0.672,
    avg: 0.743,
    rank: 4,
  },
  {
    sourceOrder: 5,
    model: "Grok Imagine 1.5",
    projectUrl: "https://x.ai/grok",
    organization: "xAI",
    organizationIcon: "assets/institutions/grok.png",
    interface: "Prompt I2V",
    render: 0.851,
    physicalObs: 0.606,
    explore: 0.764,
    intent: 0.802,
    physicalTrans: 0.667,
    drift: 0.791,
    returnScore: 0.709,
    offscreen: 0.645,
    avg: 0.734,
    rank: 5,
  },
  {
    sourceOrder: 6,
    model: "FLUX 3",
    projectUrl: "https://blackforestlabs.ai/",
    organization: "Black Forest Labs",
    organizationIcon: "assets/institutions/flux.png",
    interface: "Prompt I2V",
    render: 0.817,
    physicalObs: 0.616,
    explore: 0.764,
    intent: 0.790,
    physicalTrans: 0.632,
    drift: 0.771,
    returnScore: 0.702,
    offscreen: 0.674,
    avg: 0.722,
    rank: 6,
  },
  {
    sourceOrder: 7,
    model: "Cosmos3-Super",
    projectUrl: "https://www.nvidia.com/en-us/ai/cosmos/",
    organization: "NVIDIA",
    organizationIcon: "assets/institutions/nvidia-sil.png",
    interface: "Prompt I2V",
    render: 0.835,
    physicalObs: 0.610,
    explore: 0.779,
    intent: 0.751,
    physicalTrans: 0.602,
    drift: 0.776,
    returnScore: 0.706,
    offscreen: 0.668,
    avg: 0.719,
    rank: 7,
  },
  {
    sourceOrder: 8,
    model: "HunyuanVideo 1.5",
    projectUrl: "https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5",
    organization: "Tencent Hunyuan",
    organizationIcon: "assets/institutions/tencent-hunyuan.png",
    interface: "Prompt I2V",
    render: 0.800,
    physicalObs: 0.590,
    explore: 0.776,
    intent: 0.732,
    physicalTrans: 0.572,
    drift: 0.765,
    returnScore: 0.695,
    offscreen: 0.632,
    avg: 0.703,
    rank: 8,
  },
  {
    sourceOrder: 9,
    model: "LingBot World v2",
    projectUrl: "https://technology.robbyant.com/lingbot-world-v2",
    organization: "Robbyant",
    organizationIcon: "assets/institutions/robbyant.png",
    interface: "Camera pose",
    render: 0.805,
    physicalObs: 0.633,
    explore: 0.815,
    intent: 0.568,
    physicalTrans: 0.498,
    drift: 0.795,
    returnScore: 0.758,
    offscreen: 0.661,
    avg: 0.688,
    rank: 9,
  },
  {
    sourceOrder: 10,
    model: "SANA-WM",
    projectUrl: "https://nvlabs.github.io/Sana/WM/",
    organization: "NVIDIA",
    organizationIcon: "assets/institutions/nvlabs.jpg",
    interface: "Native action",
    render: 0.810,
    physicalObs: 0.623,
    explore: 0.825,
    intent: 0.506,
    physicalTrans: 0.476,
    drift: 0.789,
    returnScore: 0.788,
    offscreen: 0.723,
    avg: 0.687,
    rank: 10,
  },
  {
    sourceOrder: 11,
    model: "Wan 2.2",
    projectUrl: "https://wan.video/",
    organization: "Wan / Alibaba Cloud",
    organizationIcon: "assets/institutions/wan-video.png",
    interface: "Prompt I2V",
    render: 0.804,
    physicalObs: 0.586,
    explore: 0.772,
    intent: 0.620,
    physicalTrans: 0.551,
    drift: 0.760,
    returnScore: 0.665,
    offscreen: 0.634,
    avg: 0.677,
    rank: 11,
  },
  {
    sourceOrder: 12,
    model: "HY-WorldPlay 1.5",
    projectUrl: "https://3d-models.hunyuan.tencent.com/world/",
    organization: "Tencent Hunyuan",
    organizationIcon: "assets/institutions/tencent-hunyuan.png",
    interface: "Camera pose",
    render: 0.794,
    physicalObs: 0.646,
    explore: 0.820,
    intent: 0.499,
    physicalTrans: 0.455,
    drift: 0.793,
    returnScore: 0.819,
    offscreen: 0.611,
    avg: 0.671,
    rank: 12,
  },
  {
    sourceOrder: 13,
    model: "DreamX-World",
    projectUrl: "https://amap-ml.github.io/DreamX_World/",
    organization: "AMAP-ML / DreamX Team",
    organizationIcon: "assets/institutions/amap-ml.png",
    interface: "Native action",
    render: 0.785,
    physicalObs: 0.606,
    explore: 0.818,
    intent: 0.500,
    physicalTrans: 0.474,
    drift: 0.775,
    returnScore: 0.731,
    offscreen: 0.654,
    avg: 0.668,
    rank: 13,
  },
  {
    sourceOrder: 14,
    model: "ABot-World",
    projectUrl: "https://amap-cvlab.github.io/ABot-World/",
    organization: "AMAP CV Lab",
    organizationIcon: "assets/institutions/amap-cvlab.png",
    interface: "Native action",
    render: 0.777,
    physicalObs: 0.608,
    explore: 0.835,
    intent: 0.490,
    physicalTrans: 0.457,
    drift: 0.763,
    returnScore: 0.720,
    offscreen: 0.608,
    avg: 0.661,
    rank: 14,
  },
  {
    sourceOrder: 15,
    model: "Lyra 2",
    projectUrl: "https://research.nvidia.com/labs/sil/projects/lyra2/",
    organization: "NVIDIA Spatial Intelligence Lab",
    organizationIcon: "assets/institutions/nvidia-sil.png",
    interface: "Camera pose",
    render: 0.795,
    physicalObs: 0.640,
    explore: 0.807,
    intent: 0.489,
    physicalTrans: 0.451,
    drift: 0.776,
    returnScore: 0.797,
    offscreen: 0.564,
    avg: 0.655,
    rank: 15,
  },
  {
    sourceOrder: 16,
    model: "LTX-2.3",
    projectUrl: "https://ltx.io/model/ltx-2-3",
    organization: "Lightricks / LTX",
    organizationIcon: "assets/institutions/lightricks.jpg",
    interface: "Prompt I2V",
    render: 0.784,
    physicalObs: 0.545,
    explore: 0.738,
    intent: 0.604,
    physicalTrans: 0.533,
    drift: 0.724,
    returnScore: 0.633,
    offscreen: 0.577,
    avg: 0.646,
    rank: 16,
  },
  {
    sourceOrder: 17,
    model: "Fantasy-World",
    projectUrl: "https://fantasy-amap.github.io/fantasy-world/",
    organization: "AMAP, Alibaba Group",
    organizationIcon: "assets/institutions/fantasy-amap.png",
    interface: "Camera pose",
    render: 0.741,
    physicalObs: 0.627,
    explore: 0.732,
    intent: 0.524,
    physicalTrans: 0.489,
    drift: 0.699,
    returnScore: 0.684,
    offscreen: 0.538,
    avg: 0.621,
    rank: 17,
  },
  {
    sourceOrder: 18,
    model: "InSpatio-World",
    projectUrl: "https://inspatio.github.io/inspatio-world/",
    organization: "InSpatio Team",
    organizationIcon: "assets/institutions/inspatio.jpg",
    interface: "Camera pose",
    render: 0.790,
    physicalObs: 0.630,
    explore: 0.707,
    intent: 0.486,
    physicalTrans: 0.456,
    drift: 0.745,
    returnScore: 0.770,
    offscreen: 0.540,
    avg: 0.614,
    rank: 18,
  },
];

const publicSet100Scores = [
  { model: "Seedance 2.0", render: 0.846, physicalObs: 0.623, explore: 0.803, intent: 0.843, physicalTrans: 0.738, drift: 0.809, returnScore: 0.773, offscreen: 0.699, avg: 0.796 },
  { model: "Kling 3.0", render: 0.829, physicalObs: 0.613, explore: 0.796, intent: 0.848, physicalTrans: 0.725, drift: 0.761, returnScore: 0.761, offscreen: 0.673, avg: 0.786 },
  { model: "Wan 2.7", render: 0.821, physicalObs: 0.586, explore: 0.792, intent: 0.835, physicalTrans: 0.771, drift: 0.754, returnScore: 0.690, offscreen: 0.674, avg: 0.777 },
  { model: "MiniMax H3", render: 0.831, physicalObs: 0.613, explore: 0.778, intent: 0.811, physicalTrans: 0.790, drift: 0.753, returnScore: 0.725, offscreen: 0.720, avg: 0.775 },
  { model: "Grok Imagine 1.5", render: 0.863, physicalObs: 0.607, explore: 0.764, intent: 0.865, physicalTrans: 0.748, drift: 0.796, returnScore: 0.713, offscreen: 0.641, avg: 0.774 },
  { model: "Cosmos3-Super", render: 0.843, physicalObs: 0.618, explore: 0.780, intent: 0.807, physicalTrans: 0.633, drift: 0.789, returnScore: 0.715, offscreen: 0.669, avg: 0.759 },
  { model: "FLUX 3", render: 0.816, physicalObs: 0.629, explore: 0.761, intent: 0.787, physicalTrans: 0.744, drift: 0.768, returnScore: 0.705, offscreen: 0.685, avg: 0.755 },
  { model: "HunyuanVideo 1.5", render: 0.807, physicalObs: 0.590, explore: 0.773, intent: 0.781, physicalTrans: 0.580, drift: 0.764, returnScore: 0.714, offscreen: 0.625, avg: 0.740 },
  { model: "LingBot World v2", render: 0.827, physicalObs: 0.630, explore: 0.818, intent: 0.597, physicalTrans: 0.547, drift: 0.798, returnScore: 0.766, offscreen: 0.719, avg: 0.732 },
  { model: "SANA-WM", render: 0.821, physicalObs: 0.628, explore: 0.828, intent: 0.527, physicalTrans: 0.497, drift: 0.810, returnScore: 0.793, offscreen: 0.760, avg: 0.723 },
  { model: "HY-WorldPlay 1.5", render: 0.806, physicalObs: 0.651, explore: 0.805, intent: 0.506, physicalTrans: 0.479, drift: 0.813, returnScore: 0.830, offscreen: 0.671, avg: 0.707 },
  { model: "DreamX-World", render: 0.801, physicalObs: 0.604, explore: 0.819, intent: 0.519, physicalTrans: 0.511, drift: 0.775, returnScore: 0.741, offscreen: 0.675, avg: 0.705 },
  { model: "Wan 2.2", render: 0.811, physicalObs: 0.584, explore: 0.768, intent: 0.648, physicalTrans: 0.559, drift: 0.753, returnScore: 0.674, offscreen: 0.670, avg: 0.705 },
  { model: "ABot-World", render: 0.793, physicalObs: 0.607, explore: 0.844, intent: 0.486, physicalTrans: 0.441, drift: 0.758, returnScore: 0.750, offscreen: 0.644, avg: 0.700 },
  { model: "Lyra 2", render: 0.814, physicalObs: 0.639, explore: 0.811, intent: 0.490, physicalTrans: 0.453, drift: 0.799, returnScore: 0.801, offscreen: 0.629, avg: 0.697 },
  { model: "LTX-2.3", render: 0.790, physicalObs: 0.546, explore: 0.729, intent: 0.646, physicalTrans: 0.560, drift: 0.714, returnScore: 0.642, offscreen: 0.606, avg: 0.677 },
  { model: "Fantasy-World", render: 0.753, physicalObs: 0.637, explore: 0.737, intent: 0.548, physicalTrans: 0.542, drift: 0.705, returnScore: 0.686, offscreen: 0.575, avg: 0.661 },
  { model: "InSpatio-World", render: 0.810, physicalObs: 0.630, explore: 0.717, intent: 0.489, physicalTrans: 0.458, drift: 0.757, returnScore: 0.780, offscreen: 0.577, avg: 0.647 },
];

const publicSet100LeaderboardRows = publicSet100Scores.map((scores, index) => {
  const model = leaderboardRows.find((row) => row.model === scores.model);
  if (!model) throw new Error(`Missing leaderboard metadata for ${scores.model}`);
  return { ...model, ...scores, sourceOrder: index + 1, rank: index + 1 };
});

let activeLeaderboardRows = publicSet100LeaderboardRows;

const leaderboardMetricKeys = [
  "render",
  "physicalObs",
  "explore",
  "intent",
  "physicalTrans",
  "drift",
  "returnScore",
  "offscreen",
  "avg",
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
      { key: "explore", label: "Trans-E", longLabel: "Exploratory transition" },
      { key: "intent", label: "Trans-I", longLabel: "Intentional transition" },
      { key: "physicalTrans", label: "Trans-P", longLabel: "Physical transition" },
    ],
  },
  {
    id: "persistence",
    label: "World Persistence",
    metrics: [
      { key: "drift", label: "Pers-D", longLabel: "Drift resistance" },
      { key: "returnScore", label: "Pers-R", longLabel: "Return consistency" },
      { key: "offscreen", label: "Pers-O", longLabel: "Offscreen evolution" },
    ],
  },
  {
    id: "summary",
    label: "Summary",
    metrics: [{ key: "avg", label: "Overall", longLabel: "Overall score" }],
  },
];

const leaderboardMetrics = metricGroups.flatMap((group) =>
  group.metrics.map((metric) => ({ ...metric, groupId: group.id, groupLabel: group.label })),
);

let leaderboardMedalRanks = {};
let leaderboardMetricRanks = {};

function syncLeaderboardRankings() {
  const rankedRows = (metric, limit) =>
    activeLeaderboardRows
      .filter((row) => row[metric.key] != null)
      .sort((a, b) => b[metric.key] - a[metric.key] || a.sourceOrder - b.sourceOrder)
      .slice(0, limit)
      .map((row, index) => [row.sourceOrder, index + 1]);

  leaderboardMedalRanks = Object.fromEntries(
    leaderboardMetrics.map((metric) => [metric.key, new Map(rankedRows(metric, 3))]),
  );
  leaderboardMetricRanks = Object.fromEntries(
    leaderboardMetrics.map((metric) => [metric.key, new Map(rankedRows(metric, activeLeaderboardRows.length))]),
  );
}

const typeLabels = {
  semantic: "Semantic",
  navigation: "Navigation",
  physical: "Physics",
  persistence: "Persistence",
  exploratory: "Exploration",
  intentional: "Intentional",
  drift_resistance: "Drift Resistance",
  exploratory_transition: "Exploratory transition",
  intentional_transition: "Intentional Transition",
  offscreen_evolution: "Offscreen evolution",
  physical_transition: "Physical Transition",
  return_revisit_consistency: "Return Revisit Consistency",
};

const STATIC_GALLERY_ENDPOINT = "./assets/data/gallery-static.json";
const GALLERY_PAGE_SIZE = 12;
const outputState = {
  all: [],
  filtered: [],
  families: [],
  familyOrder: {},
  filter: "all",
  query: "",
  sort: "family",
  visible: GALLERY_PAGE_SIZE,
  activeIndex: 0,
  activeCase: null,
  activeResult: null,
  activeRequest: "",
  loaded: false,
  loading: false,
};
const leaderboardState = {
  sortKey: "avg",
  direction: "desc",
  query: "",
  interface: "all",
  groups: new Set(metricGroups.map((group) => group.id)),
};
let timelineState = "public-100";
const timelineStates = {
  release: {
    label: "2026-08-18 V1",
    progress: "0%",
    rows: leaderboardRows,
  },
  "public-100": {
    label: "2026-09-01 Public Set",
    progress: "50%",
    rows: publicSet100LeaderboardRows,
  },
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function refreshIcons(root = document) {
  if (window.lucide) window.lucide.createIcons({ attrs: { "stroke-width": 1.8 }, root });
}

async function copyTextToClipboard(value) {
  if (navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(value);
      return;
    } catch {
      // Fall through for browsers that expose the API without granting clipboard access.
    }
  }

  const textArea = document.createElement("textarea");
  textArea.value = value;
  textArea.setAttribute("readonly", "");
  textArea.style.position = "fixed";
  textArea.style.inset = "0 auto auto 0";
  textArea.style.opacity = "0";
  textArea.style.pointerEvents = "none";
  document.body.append(textArea);
  textArea.select();

  try {
    if (!document.execCommand("copy")) throw new Error("Copy command was rejected");
  } finally {
    textArea.remove();
  }
}

function setupBibtexCopy() {
  const button = document.querySelector("[data-bibtex-copy]");
  const code = document.querySelector("[data-bibtex-code]");
  const label = button?.querySelector("[data-bibtex-copy-label]");
  if (!button || !code || !label) return;

  let resetTimer = 0;
  const setState = (state) => {
    const copied = state === "copied";
    const failed = state === "error";
    button.classList.toggle("is-copied", copied);
    button.classList.toggle("is-error", failed);
    label.textContent = copied ? "Copied" : failed ? "Try again" : "Copy";
    const accessibleLabel = copied
      ? "BibTeX citation copied"
      : failed
        ? "Copy failed, try again"
        : "Copy BibTeX citation";
    button.setAttribute("aria-label", accessibleLabel);
    button.title = accessibleLabel;
  };

  button.addEventListener("click", async () => {
    window.clearTimeout(resetTimer);
    button.disabled = true;
    try {
      await copyTextToClipboard(code.textContent.trim());
      setState("copied");
    } catch {
      setState("error");
    } finally {
      button.disabled = false;
      resetTimer = window.setTimeout(() => setState("idle"), 2400);
    }
  });
}

function setupHeroShowcase() {
  const grid = document.querySelector("[data-hero-grid]");
  const tiles = [...document.querySelectorAll("[data-hero-tile]")];
  if (!grid || tiles.length !== 6 || heroImageSets.some((set) => set.length !== tiles.length)) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const saveData = navigator.connection?.saveData === true;
  if (reducedMotion.matches || saveData) {
    grid.dataset.motion = "frozen";
    return;
  }

  const cycleMs = 7000;
  const fadeMs = 820;
  const staggerMs = 130;
  const transitionMs = fadeMs + staggerMs * (tiles.length - 1);
  const imageCache = new Map();
  let activeSet = 0;
  let timer = null;
  let transitioning = false;
  let frozen = false;

  const loadImage = (item) => {
    if (imageCache.has(item.src)) return imageCache.get(item.src);
    const promise = (async () => {
      const image = new Image();
      image.alt = "";
      image.width = 960;
      image.height = 540;
      image.decoding = "async";
      const loaded = new Promise((resolve, reject) => {
        image.addEventListener("load", resolve, { once: true });
        image.addEventListener("error", reject, { once: true });
      });
      image.src = item.src;
      try {
        if (typeof image.decode === "function") await image.decode();
        else await loaded;
      } catch {
        try {
          await loaded;
        } catch {
          return null;
        }
      }
      return image.naturalWidth ? image : null;
    })();
    imageCache.set(item.src, promise);
    return promise;
  };

  const preloadSet = (index) => Promise.all(heroImageSets[index].map(loadImage));

  const schedule = (delay = cycleMs) => {
    window.clearTimeout(timer);
    if (frozen || document.hidden) return;
    timer = window.setTimeout(runCycle, delay);
  };

  const transitionTo = async (nextSet) => {
    transitioning = true;
    const items = heroImageSets[nextSet];
    const images = await preloadSet(nextSet);
    if (images.some((image) => !image) || document.hidden || frozen) {
      transitioning = false;
      return false;
    }

    const previousImages = tiles.map((tile) => tile.querySelector(".hero-tile-image.is-active"));
    images.forEach((image, index) => {
      image.className = "hero-tile-image";
      image.style.transitionDelay = `${index * staggerMs}ms`;
      tiles[index].append(image);
      tiles[index].dataset.caseId = items[index].caseId;
      if (previousImages[index]) previousImages[index].style.transitionDelay = `${index * staggerMs}ms`;
    });

    await new Promise((resolve) => window.requestAnimationFrame(() => window.requestAnimationFrame(resolve)));
    images.forEach((image, index) => {
      image.classList.add("is-active");
      previousImages[index]?.classList.remove("is-active");
      previousImages[index]?.classList.add("is-leaving");
    });

    await new Promise((resolve) => window.setTimeout(resolve, transitionMs + 80));
    previousImages.forEach((image) => image?.remove());
    images.forEach((image) => {
      image.classList.remove("is-leaving");
      image.style.transitionDelay = "";
    });
    activeSet = nextSet;
    transitioning = false;
    return true;
  };

  async function runCycle() {
    if (transitioning || frozen || document.hidden) {
      schedule();
      return;
    }
    await transitionTo((activeSet + 1) % heroImageSets.length);
    schedule(Math.max(1000, cycleMs - transitionMs));
  }

  const preloadRemaining = () => {
    heroImageSets.slice(1).forEach((_, index) => preloadSet(index + 1));
  };
  if ("requestIdleCallback" in window) {
    window.requestIdleCallback(preloadRemaining, { timeout: 4500 });
  } else {
    window.setTimeout(preloadRemaining, 1500);
  }

  document.addEventListener("visibilitychange", () => {
    window.clearTimeout(timer);
    if (!document.hidden && !frozen) schedule(cycleMs);
  });
  reducedMotion.addEventListener?.("change", (event) => {
    frozen = event.matches;
    grid.dataset.motion = frozen ? "frozen" : "active";
    if (frozen) window.clearTimeout(timer);
    else schedule(cycleMs);
  });

  grid.dataset.motion = "active";
  schedule(cycleMs);
}

function formatLeaderboardScore(value) {
  return value == null ? "--" : (Number(value) * 100).toFixed(1);
}

function leaderboardActiveMetricGroups() {
  const groups = metricGroups.filter((group) => leaderboardState.groups.has(group.id));
  return groups.length ? groups : metricGroups.filter((group) => group.id === "summary");
}

function leaderboardActiveMetrics() {
  return leaderboardActiveMetricGroups().flatMap((group) => group.metrics);
}

function leaderboardMetricLabel(key) {
  if (key === "rank") return "Rank";
  if (key === "model") return "Model";
  if (key === "interface") return "Interface";
  return leaderboardMetrics.find((metric) => metric.key === key)?.label || key;
}

function leaderboardPreferredDirection(key) {
  if (key === "rank" || key === "model" || key === "interface") return "asc";
  return "desc";
}

function ensureLeaderboardVisibleSort() {
  if (["rank", "model", "interface"].includes(leaderboardState.sortKey)) return;
  if (leaderboardActiveMetrics().some((metric) => metric.key === leaderboardState.sortKey)) return;

  const firstMetric = leaderboardActiveMetrics()[0] || leaderboardMetrics.find((metric) => metric.key === "avg");
  leaderboardState.sortKey = firstMetric.key;
  leaderboardState.direction = leaderboardPreferredDirection(firstMetric.key);
}

function leaderboardSortValue(row, key) {
  if (key === "model") return row.model;
  if (key === "interface") return row.interface;
  return row[key];
}

function compareLeaderboardRows(a, b) {
  const left = leaderboardSortValue(a, leaderboardState.sortKey);
  const right = leaderboardSortValue(b, leaderboardState.sortKey);
  const direction = leaderboardState.direction === "asc" ? 1 : -1;

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

function rowSearchText(row) {
  return [row.model, row.organization, row.interface].join(" ").toLowerCase();
}

function filteredLeaderboardRows() {
  const query = leaderboardState.query.trim().toLowerCase();
  return activeLeaderboardRows
    .filter((row) => leaderboardState.interface === "all" || row.interface === leaderboardState.interface)
    .filter((row) => !query || rowSearchText(row).includes(query))
    .sort(compareLeaderboardRows);
}

function leaderboardSortButton(key, label, title = "") {
  const active = leaderboardState.sortKey === key;
  const icon = active
    ? ` <i data-sort-indicator data-lucide="arrow-${leaderboardState.direction === "asc" ? "up" : "down"}" aria-hidden="true"></i>`
    : "";
  return `<button type="button" data-sort-key="${escapeHtml(key)}" title="${escapeHtml(title || `Sort by ${label}`)}">${escapeHtml(label)}${icon}</button>`;
}

function leaderboardAriaSort(key) {
  if (leaderboardState.sortKey !== key) return "none";
  return leaderboardState.direction === "asc" ? "ascending" : "descending";
}

function renderLeaderboardHeader() {
  const head = document.querySelector("[data-leaderboard-head]");
  if (!head) return;

  const groups = leaderboardActiveMetricGroups();
  head.innerHTML = `
    <tr class="group-row">
      <th rowspan="2" scope="col" class="rank-column" aria-sort="${leaderboardAriaSort("rank")}">
        ${leaderboardSortButton("rank", "Rank")}
      </th>
      <th rowspan="2" scope="col" class="model-column" aria-sort="${leaderboardAriaSort("model")}">
        ${leaderboardSortButton("model", "Model")}
      </th>
      <th rowspan="2" scope="col" class="interface-column" aria-sort="${leaderboardAriaSort("interface")}">
        ${leaderboardSortButton("interface", "Interface")}
      </th>
      ${groups
        .map((group) => `<th colspan="${group.metrics.length}" scope="colgroup" class="metric-group">${escapeHtml(group.label)}</th>`)
        .join("")}
    </tr>
    <tr class="metric-row">
      ${groups
        .flatMap((group) => group.metrics.map((metric, index) => ({ ...metric, firstInGroup: index === 0 })))
        .map(
          (metric) => `
            <th scope="col" class="${metric.firstInGroup ? "metric-first" : ""}${metric.key === "avg" ? " overall-column" : ""}" aria-sort="${leaderboardAriaSort(metric.key)}">
              ${leaderboardSortButton(metric.key, metric.label, `Sort by ${metric.longLabel}`)}
            </th>`,
        )
        .join("")}
    </tr>
  `;
}

function leaderboardInterfaceClass(value) {
  if (value === "Prompt I2V") return "interface-prompt";
  if (value === "Camera pose") return "interface-camera";
  return "interface-native";
}

function leaderboardInstitutionMark(row) {
  if (row.organizationIcon) {
    return `
      <img
        class="institution-icon"
        src="${escapeHtml(row.organizationIcon)}"
        alt=""
        width="22"
        height="22"
        aria-hidden="true"
      />`;
  }
  const initial = String(row.organization || row.model || "M").trim().charAt(0).toUpperCase();
  return `<span class="institution-icon institution-icon-fallback" aria-hidden="true">${escapeHtml(initial)}</span>`;
}

function scoreCell(row, metric, firstInGroup = false) {
  const value = row[metric.key];
  const medalRank = leaderboardMedalRanks[metric.key].get(row.sourceOrder);
  const metricRank = leaderboardMetricRanks[metric.key].get(row.sourceOrder);
  const medalClass = medalRank ? ["gold", "silver", "bronze"][medalRank - 1] : "";
  const classes = [
    "score-cell",
    firstInGroup ? "metric-first" : "",
    metric.key === "avg" ? "overall-cell" : "",
    value == null ? "missing" : "",
    medalClass ? `podium-cell podium-${medalClass}` : "",
  ]
    .filter(Boolean)
    .join(" ");

  if (value == null) return `<td class="${classes}">--</td>`;

  const medalLabel = medalRank ? `${["Gold", "Silver", "Bronze"][medalRank - 1]} medal, rank ${medalRank}` : "";
  const medal = medalRank
    ? `<span class="score-medal" role="img" aria-label="${medalLabel}" title="${medalLabel}"><i data-lucide="medal" aria-hidden="true"></i></span>`
    : "";

  return `
    <td class="${classes}">
      <span class="score-entry">
        <span class="score-line">${medal}<span class="score-value">${formatLeaderboardScore(value)}</span></span>
        <span class="score-rank">#${metricRank}</span>
      </span>
    </td>`;
}

function renderLeaderboardRows() {
  const body = document.querySelector("[data-leaderboard-body]");
  if (!body) return;

  const rows = filteredLeaderboardRows();
  const groups = leaderboardActiveMetricGroups();
  const metrics = groups.flatMap((group) =>
    group.metrics.map((metric, index) => ({ ...metric, firstInGroup: index === 0 })),
  );

  body.innerHTML = rows
    .map((row) => {
      return `
        <tr class="leaderboard-row" data-row-id="${row.sourceOrder}">
          <td class="rank-cell${row.rank == null ? " missing" : ""}">
            <span class="rank-number">${row.rank == null ? "--" : escapeHtml(row.rank)}</span>
          </td>
          <td class="model-cell">
            <a
              class="model-link"
              href="${escapeHtml(row.projectUrl)}"
              target="_blank"
              rel="noopener noreferrer"
              title="Open ${escapeHtml(row.model)} project page (${escapeHtml(row.organization)})"
              aria-label="Open ${escapeHtml(row.model)} project page, ${escapeHtml(row.organization)}"
            >
              ${leaderboardInstitutionMark(row)}
              <span class="model-name">${escapeHtml(row.model)}</span>
            </a>
          </td>
          <td class="interface-cell">
            <span class="interface-pill ${leaderboardInterfaceClass(row.interface)}">${escapeHtml(row.interface)}</span>
          </td>
          ${metrics.map((metric) => scoreCell(row, metric, metric.firstInGroup)).join("")}
        </tr>`;
    })
    .join("");

  const summary = document.querySelector("[data-leaderboard-summary]");
  if (summary) {
    summary.textContent = `Showing ${rows.length} of ${activeLeaderboardRows.length}. Sorted by ${leaderboardMetricLabel(leaderboardState.sortKey)} ${leaderboardState.direction}.`;
  }

  const empty = document.querySelector("[data-leaderboard-empty]");
  if (empty) empty.hidden = rows.length > 0;

  refreshIcons(body);
}

function renderLeaderboard() {
  ensureLeaderboardVisibleSort();
  renderLeaderboardHeader();
  renderLeaderboardRows();
  refreshIcons(document.querySelector(".leaderboard-table"));
}

function syncTimeline() {
  const timeline = timelineStates[timelineState] || timelineStates.release;
  const headDate = document.querySelector("[data-timeline-head-date]");
  const progress = document.querySelector("[data-timeline-progress]");
  const releaseStamp = document.querySelector("[data-release-stamp]");

  if (headDate) headDate.textContent = timeline.label;
  if (progress) progress.style.width = timeline.progress;
  if (releaseStamp) releaseStamp.textContent = timeline.label;

  document.querySelectorAll("[data-timeline-choice]").forEach((button) => {
    const active = button.dataset.timelineChoice === timelineState;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-pressed", String(active));
  });
}

function setTimeline(choice) {
  if (!timelineStates[choice]) return;
  timelineState = choice;
  activeLeaderboardRows = timelineStates[choice].rows;
  syncLeaderboardRankings();
  resetLeaderboardState();
  syncLeaderboardControls();
  syncTimeline();
  renderLeaderboard();
}

function caseSearchText(item) {
  return [
    item.id,
    item.family,
    item.axis,
    item.title,
    item.scene,
    item.style,
    item.perspective,
    item.subject,
    item.prompt,
    item.cohort,
  ]
    .join(" ")
    .toLowerCase();
}

function compareCasesByFamily(a, b, familyOrder = outputState.familyOrder) {
  return ((familyOrder[a.family] ?? 999) - (familyOrder[b.family] ?? 999)) || a.id.localeCompare(b.id);
}

function familyLabel(value) {
  if (typeLabels[value]) return typeLabels[value];
  return String(value || "Unknown")
    .split(/[_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function detailCaseId(value) {
  const parts = String(value || "").split("_");
  if (parts.length >= 3) return familyLabel(parts.slice(1, 3).join("_"));
  return familyLabel(value);
}

function outputCaseId(value) {
  const text = String(value || "");
  const match = text.match(/(?:^|_)initial_(\d{3,5})(?:_|$)/i);
  if (match) return `Initial ${match[1]}`;
  return detailCaseId(text);
}

function formatScore(value) {
  return typeof value === "number" && Number.isFinite(value) ? value.toFixed(3) : "-";
}

function isZeroScore(value) {
  return typeof value === "number" && Number.isFinite(value) && value === 0;
}

function zeroScoreClass(value) {
  return isZeroScore(value) ? " is-zero-score" : "";
}

function renderCaseFilterButtons(families = []) {
  const list = document.querySelector("[data-case-filter-list]");
  if (!list) return;
  const buttons = [
    `<button type="button" class="${outputState.filter === "all" ? "is-active" : ""}" aria-pressed="${outputState.filter === "all"}" data-case-filter="all">All <span>${outputState.all.length}</span></button>`,
    ...families.map((family) => {
      const count = typeof family.count === "number" ? ` <span>${family.count}</span>` : "";
      const active = outputState.filter === family.id;
      return `<button type="button" class="${active ? "is-active" : ""}" aria-pressed="${active}" data-case-filter="${escapeHtml(family.id)}">${escapeHtml(family.label || familyLabel(family.id))}${count}</button>`;
    }),
  ];
  list.innerHTML = buttons.join("");
}

function closeDialog(dialog) {
  if (dialog?.open) dialog.close();
}

function outputActionChunkItems(chunks = []) {
  return chunks.filter((chunk) => chunk?.id || chunk?.actions?.length);
}

function outputActionChunkMarkup(chunk) {
  const actions = (chunk.actions || []).join(" + ") || "-";
  return `<span><code>${escapeHtml(chunk.id || "step")}</code>${escapeHtml(actions)}</span>`;
}

function outputCard(item, index) {
  const rawActionText = String(item.action?.text || "").trim();
  const actionText = /^no action text available\.?$/i.test(rawActionText) ? "" : rawActionText;
  const actionChunks = outputActionChunkItems(item.action?.chunks || []);
  const actionSummary = actionText
    ? `<p>${escapeHtml(actionText)}</p>`
    : actionChunks.length
      ? `<div class="output-card-action-sequence" aria-label="Action sequence">${actionChunks.map(outputActionChunkMarkup).join("")}</div>`
      : "";
  const scoreText = formatScore(item.meanScore);
  return `
    <article class="output-card">
      <button class="output-card-button" type="button" data-output-index="${index}" aria-label="Open ${escapeHtml(item.title)} details"></button>
      <div class="output-card-surface">
        <div class="output-card-media">
          ${item.poster ? `<img src="${escapeHtml(item.poster)}" alt="${escapeHtml(item.title)} initial observation" loading="lazy" decoding="async" fetchpriority="${index < 3 ? "high" : "auto"}" />` : ""}
          <span class="card-type">${escapeHtml(typeLabels[item.family] || familyLabel(item.family))}</span>
          <span class="output-score">${escapeHtml(scoreText)}</span>
          <span class="play-overlay" aria-hidden="true"><span><i data-lucide="play"></i></span></span>
        </div>
        <div class="output-card-content">
          <code>${escapeHtml(outputCaseId(item.id))}</code>
          <div class="output-card-title-row">
            <h3>${escapeHtml(item.title)}</h3>
            <button class="evidence-tree-link" type="button" data-output-evidence-index="${index}" aria-label="Open ${escapeHtml(item.title)} Evidence Tree">
              <i data-lucide="git-branch" aria-hidden="true"></i>
              Evidence Tree
              <i class="evidence-cta-arrow" data-lucide="arrow-right" aria-hidden="true"></i>
            </button>
          </div>
          ${actionSummary}
        </div>
      </div>
    </article>`;
}

function applyOutputFilters() {
  const query = outputState.query.trim().toLowerCase();
  outputState.filtered = outputState.all.filter((item) => {
    const familyMatch = outputState.filter === "all" || item.family === outputState.filter;
    return familyMatch && (!query || caseSearchText(item).includes(query));
  });

  outputState.filtered.sort((a, b) => {
    if (outputState.sort === "id") return a.id.localeCompare(b.id);
    if (outputState.sort === "scene") return (a.scene || a.title).localeCompare(b.scene || b.title);
    if (outputState.sort === "score") return (b.meanScore ?? -Infinity) - (a.meanScore ?? -Infinity);
    return compareCasesByFamily(a, b, outputState.familyOrder);
  });
  renderOutputs();
}

function renderOutputs() {
  const grid = document.querySelector("[data-output-grid]");
  const count = document.querySelector("[data-output-count]");
  const loadMore = document.querySelector("[data-output-load-more]");
  if (!grid || !loadMore) return;
  const shown = outputState.filtered.slice(0, outputState.visible);

  if (!shown.length) {
    grid.innerHTML = `
      <div class="empty-gallery">
        <strong>No matching cases</strong>
        <p>Try a different category or search term.</p>
      </div>`;
  } else {
    grid.innerHTML = shown.map(outputCard).join("");
  }

  if (count) count.textContent = `Showing ${shown.length} of ${outputState.filtered.length} matching cases`;
  loadMore.hidden = shown.length >= outputState.filtered.length;
  refreshIcons(grid);
}

function renderOutputActionChunks(dialog, chunks = []) {
  const target = dialog.querySelector("[data-output-action-chunks]");
  if (!target) return;
  const items = outputActionChunkItems(chunks);
  target.hidden = !items.length;
  target.innerHTML = items.map(outputActionChunkMarkup).join("");
}

function outputResultBySlug(caseItem, modelSlug) {
  return caseItem?.results?.find((result) => (result.modelSlug || result.model) === modelSlug);
}

function renderOutputResultRows(caseItem) {
  const rows = document.querySelector("[data-output-result-rows]");
  if (!rows) return;
  rows.innerHTML = (caseItem.results || [])
    .map((result) => {
      const modelKey = result.modelSlug || result.model;
      const activeKey = outputState.activeResult?.modelSlug || outputState.activeResult?.model;
      const active = modelKey === activeKey;
      return `
        <tr class="output-result-row${active ? " is-active" : ""}"
            tabindex="0"
            aria-label="Play ${escapeHtml(result.model || result.modelSlug)} result and show model details"
            aria-selected="${active}"
            data-output-result-model="${escapeHtml(modelKey)}">
          <td>${escapeHtml(result.model || result.modelSlug)}</td>
          <td class="${zeroScoreClass(result.score).trim()}">${escapeHtml(formatScore(result.score))}</td>
        </tr>`;
    })
    .join("");
}

function outputCssToken(value) {
  return String(value || "unknown").toLowerCase().replace(/[^a-z0-9_-]+/g, "-");
}

function outputSkillId(skill) {
  return skill?.id || skill?.skill_id || "skill";
}

function outputSkillPlan(caseItem, detailedScore = null) {
  const casePlan = caseItem?.skillPlan || {};
  const detailedPlan = detailedScore?.skill_plan || {};
  return {
    routingMode: detailedPlan.routing_mode || casePlan.routingMode,
    selectedSkillIds: detailedPlan.selected_skill_ids || casePlan.selectedSkillIds || [],
    coreSkillIds: detailedPlan.core_skill_ids || casePlan.coreSkillIds || [],
    skippedSkills: casePlan.skippedSkills || [],
  };
}

function outputDetailText(value) {
  if (value == null || value === "") return "-";
  if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(4);
  if (Array.isArray(value)) return value.every((item) => item == null || ["string", "number", "boolean"].includes(typeof item))
    ? value.map(outputDetailText).join(", ")
    : `${value.length} records`;
  if (typeof value === "object") return `${Object.keys(value).length} fields`;
  return String(value);
}

function renderOutputReasoningSummary(caseItem, result, detailedScore = null, error = "") {
  document.querySelector("[data-output-reasoning-model]").textContent = result.model || result.modelSlug || "Model result";
  const score = document.querySelector("[data-output-reasoning-score]");
  score.textContent = formatScore(result.score);
  score.classList.toggle("is-zero-score", isZeroScore(result.score));
  document.querySelector("[data-output-reasoning-state]").textContent = error || (detailedScore ? "Evidence loaded" : "Loading evidence");
}

function outputKeyValuePanel(title, source) {
  const entries = Object.entries(source || {});
  return `
    <section class="output-keyvalue-panel">
      <h4>${escapeHtml(title)}</h4>
      ${
        entries.length
          ? `<div>${entries.map(([key, value]) => `<div><span title="${escapeHtml(key)}">${escapeHtml(key)}</span><strong class="${zeroScoreClass(value).trim()}">${escapeHtml(outputDetailText(value))}</strong></div>`).join("")}</div>`
          : `<p>No ${escapeHtml(title.toLowerCase())}</p>`
      }
    </section>`;
}

function outputVideoJudgmentMetrics(detail) {
  const evidence = Object.values(detail?.diagnostics?.v2_evidence || {}).find(
    (stage) => String(stage?.stage || "").toLowerCase() === "video_judgment",
  );
  if (!evidence) return outputKeyValuePanel("VLM evidence, reasoning, scores", detail?.metrics || {});

  const judgment = evidence.judgment || {};
  const questions = evidence.questions || {};
  const scores = judgment.q_scores || {};
  const reasons = judgment.reasons || {};
  const recordedItems = Array.isArray(evidence.question_evidence) ? evidence.question_evidence : [];
  const items = recordedItems.length
    ? recordedItems
    : Object.entries(scores).map(([id, score]) => ({ id, score, question: questions[id], reason: reasons[id] }));

  return `
    <section class="output-keyvalue-panel output-video-judgment-metrics">
      <h4>VLM evidence, reasoning, scores</h4>
      ${judgment.summary ? `<p class="output-video-judgment-summary">${escapeHtml(judgment.summary)}</p>` : ""}
      <div class="output-video-judgment-list">
        ${items
          .map((item) => `
            <article>
              <header>
                <code>${escapeHtml(item.id || "question")}</code>
                <strong class="${zeroScoreClass(item.score).trim()}">${escapeHtml(formatScore(item.score))}</strong>
              </header>
              <p class="output-video-judgment-question">${escapeHtml(item.question || questions[item.id] || "-")}</p>
              <p class="output-video-judgment-reason">${escapeHtml(item.reason || reasons[item.id] || "No reason recorded")}</p>
            </article>`)
          .join("")}
      </div>
    </section>`;
}

function outputSkillDetail(caseItem, result, summary, detail = null) {
  const id = outputSkillId(summary);
  const plan = outputSkillPlan(caseItem);
  const role = detail?.plan_role || summary.role || (plan.coreSkillIds.includes(id) || (result.coreSkills || []).includes(id) ? "core" : "evidence");
  const status = summary.status || detail?.status || "unknown";
  const reason = detail?.plan_reason || summary.reason || "Metric and diagnostic evidence";
  const isVlm = id.toLowerCase().endsWith("_vlm");
  const columns = detail
    ? `
      <div class="output-skill-columns${isVlm ? " is-vlm" : ""}">
        ${isVlm ? outputVideoJudgmentMetrics(detail) : outputKeyValuePanel("Metrics", detail.metrics || {})}
      </div>`
    : `<p class="output-skill-loading">Detailed evidence is loading.</p>`;

  return `
    <details class="output-skill-detail"${isVlm ? " open" : ""}>
      <summary>
        <span class="output-role-dot ${escapeHtml(outputCssToken(role))}"></span>
        <span class="output-skill-title">
          <strong>${escapeHtml(id)}</strong>
        </span>
        <span class="output-skill-role">${escapeHtml(role)}</span>
        <span class="output-skill-status ${escapeHtml(outputCssToken(status))}">${escapeHtml(status)}</span>
        <span class="output-skill-value${zeroScoreClass(summary.score ?? detail?.score)}">${escapeHtml(formatScore(summary.score ?? detail?.score))}</span>
      </summary>
      <div class="output-skill-body">
        <p class="output-skill-reason">${escapeHtml(reason)}</p>
        ${columns}
      </div>
    </details>`;
}

function renderOutputSkillDetails(caseItem, result, detailedScore = null) {
  const list = document.querySelector("[data-output-skill-list]");
  const count = document.querySelector("[data-output-skill-count]");
  if (!list || !count) return;
  const skills = result.skills || [];
  const detailById = new Map((detailedScore?.skills || []).map((skill) => [skill.skill_id, skill]));
  count.textContent = `${skills.length} selected / ${(caseItem.skillPlan?.skippedSkills || []).length} rejected`;
  if (!skills.length) {
    list.innerHTML = `<p>No selected skill summaries available.</p>`;
    return;
  }
  list.innerHTML = skills.map((summary) => outputSkillDetail(caseItem, result, summary, detailById.get(outputSkillId(summary)))).join("");
}

function renderOutputRejectedSkills(caseItem) {
  const list = document.querySelector("[data-output-rejected-skill-list]");
  const count = document.querySelector("[data-output-rejected-skill-count]");
  if (!list || !count) return;
  const skipped = caseItem.skillPlan?.skippedSkills || [];
  count.textContent = `${skipped.length} rejected / skipped`;
  if (!skipped.length) {
    list.innerHTML = `<p>No rejected or skipped skills.</p>`;
    return;
  }
  list.innerHTML = skipped
    .map((skill) => `
      <details class="output-skill-detail">
        <summary>
          <span class="output-role-dot rejected"></span>
          <span class="output-skill-title">
            <strong>${escapeHtml(outputSkillId(skill))}</strong>
          </span>
          <span class="output-skill-role">not routed</span>
          <span class="output-skill-status rejected">rejected</span>
          <span class="output-skill-value">-</span>
        </summary>
        <div class="output-skill-body">
          <p class="output-skill-reason">${escapeHtml(skill.reason || "No rejection reason recorded")}</p>
        </div>
      </details>`)
    .join("");
}

async function loadOutputScore(result) {
  if (!result.scorePath) return null;
  if (result.scoreDetail) return result.scoreDetail;
  const response = await fetch(result.scorePath);
  if (!response.ok) throw new Error(`score request failed with ${response.status}`);
  result.scoreDetail = await response.json();
  return result.scoreDetail;
}

async function selectOutputResult(caseItem, result, autoplay = true) {
  const dialog = document.querySelector("[data-output-dialog]");
  if (!dialog || !caseItem || !result) return;
  outputState.activeCase = caseItem;
  outputState.activeResult = result;
  const requestKey = `${caseItem.id}::${result.modelSlug || result.model}`;
  outputState.activeRequest = requestKey;
  renderOutputResultRows(caseItem);

  renderOutputReasoningSummary(caseItem, result);
  renderOutputSkillDetails(caseItem, result);
  renderOutputRejectedSkills(caseItem);

  const placeholder = dialog.querySelector("[data-output-video-placeholder]");
  const video = dialog.querySelector("[data-output-dialog-video]");
  const label = dialog.querySelector("[data-output-video-model]");
  if (video && placeholder && label) {
    video.pause();
    if (!result.video) {
      video.removeAttribute("src");
      video.load();
      video.hidden = true;
      placeholder.hidden = false;
      placeholder.textContent = "Video artifact is missing";
      label.textContent = "";
    } else {
      placeholder.hidden = true;
      video.hidden = false;
      video.poster = result.poster || caseItem.poster || caseItem.image || "";
      video.src = result.video;
      video.load();
      label.textContent = `${result.model || result.modelSlug} / ${caseItem.id}`;
      if (autoplay) video.play().catch(() => {});
    }
  }

  try {
    const detail = await loadOutputScore(result);
    if (outputState.activeRequest !== requestKey) return;
    if (!detail) {
      renderOutputReasoningSummary(caseItem, result, null, "No detailed evidence endpoint");
      renderOutputSkillDetails(caseItem, result, null);
      return;
    }
    renderOutputReasoningSummary(caseItem, result, detail);
    renderOutputSkillDetails(caseItem, result, detail);
  } catch (error) {
    if (outputState.activeRequest !== requestKey) return;
    renderOutputReasoningSummary(caseItem, result, null, `Load failed: ${error.message}`);
  }
}

function showOutputResultLoading(dialog) {
  const rows = dialog.querySelector("[data-output-result-rows]");
  if (rows) rows.innerHTML = `<tr><td class="output-result-message" colspan="2">Loading model results...</td></tr>`;

  const placeholder = dialog.querySelector("[data-output-video-placeholder]");
  const video = dialog.querySelector("[data-output-dialog-video]");
  const label = dialog.querySelector("[data-output-video-model]");
  if (video) {
    video.pause();
    video.removeAttribute("src");
    video.load();
    video.hidden = true;
  }
  if (placeholder) {
    placeholder.hidden = false;
    placeholder.textContent = "Loading model results";
  }
  if (label) label.textContent = "";

  dialog.querySelector("[data-output-reasoning-model]").textContent = "Loading model details";
  dialog.querySelector("[data-output-reasoning-score]").textContent = "-";
  dialog.querySelector("[data-output-reasoning-score]").classList.remove("is-zero-score");
  dialog.querySelector("[data-output-reasoning-state]").textContent = "Loading results";
  dialog.querySelector("[data-output-skill-count]").textContent = "Loading";
  dialog.querySelector("[data-output-skill-list]").innerHTML = "";
  dialog.querySelector("[data-output-rejected-skill-count]").textContent = "";
  dialog.querySelector("[data-output-rejected-skill-list]").innerHTML = "";
}

function scrollOutputDialogToEvidence(dialog) {
  const selectedList = dialog.querySelector("[data-output-skill-list]");
  if (!selectedList) return;
  const selectedVlm = [...selectedList.querySelectorAll(".output-skill-detail")].find((detail) =>
    detail.querySelector(".output-skill-title strong")?.textContent.trim().toLowerCase().endsWith("_vlm"),
  );
  const target = selectedVlm || selectedList;
  const dialogRect = dialog.getBoundingClientRect();
  const targetRect = target.getBoundingClientRect();
  const headerHeight = dialog.querySelector(".dialog-header")?.getBoundingClientRect().height || 0;
  dialog.scrollTo({
    top: Math.max(0, dialog.scrollTop + targetRect.top - dialogRect.top - headerHeight - 12),
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
  });
}

async function openOutputDialog(index, destination = "top") {
  const item = outputState.filtered[index];
  const dialog = document.querySelector("[data-output-dialog]");
  if (!item || !dialog) return;
  outputState.activeIndex = index;
  outputState.activeCase = item;
  outputState.activeResult = null;
  outputState.activeRequest = "";

  dialog.querySelector("[data-output-dialog-family]").textContent = typeLabels[item.family] || familyLabel(item.family);
  dialog.querySelector("[data-output-dialog-title]").textContent = item.title;
  dialog.querySelector("[data-output-dialog-case-id]").textContent = outputCaseId(item.id);
  dialog.querySelector("[data-output-dialog-input]").src = item.image || "";
  dialog.querySelector("[data-output-dialog-input]").alt = `Initial observation for ${item.title}`;
  dialog.querySelector("[data-output-action-type]").textContent = familyLabel(item.action?.type || item.family);
  dialog.querySelector("[data-output-action-text]").textContent = item.action?.text || "No action text available.";
  dialog.querySelector("[data-output-results-title]").textContent = `${item.resultCount || item.results?.length || 0}-model results`;
  const meanScore = dialog.querySelector("[data-output-mean-score]");
  meanScore.textContent = formatScore(item.meanScore);
  meanScore.classList.toggle("is-zero-score", isZeroScore(item.meanScore));
  renderOutputActionChunks(dialog, item.action?.chunks || []);

  if (item.results?.length) renderOutputResultRows(item);
  else showOutputResultLoading(dialog);

  if (!dialog.open) {
    if (typeof dialog.showModal === "function") dialog.showModal();
    else dialog.setAttribute("open", "");
  }
  dialog.scrollTop = 0;
  document.body.classList.add("dialog-open");
  refreshIcons(dialog);

  if (outputState.activeCase !== item || !dialog.open) return;
  if (!item.results?.length) {
    const rows = dialog.querySelector("[data-output-result-rows]");
    if (rows) rows.innerHTML = `<tr><td class="output-result-message" colspan="2">No static model results available.</td></tr>`;
    dialog.querySelector("[data-output-video-placeholder]").textContent = "Model results unavailable";
    dialog.querySelector("[data-output-reasoning-state]").textContent = "No static results";
    return;
  }
  dialog.querySelector("[data-output-results-title]").textContent = `${item.resultCount || item.results?.length || 0}-model results`;
  const preferredResult = item.results?.find((result) => result.video) || item.results?.[0];
  renderOutputResultRows(item);
  if (preferredResult) await selectOutputResult(item, preferredResult, true);
  if (outputState.activeCase !== item || !dialog.open) return;
  refreshIcons(dialog);
  if (destination === "evidence") {
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (outputState.activeCase === item && dialog.open) scrollOutputDialogToEvidence(dialog);
    }));
  }
}

async function loadEvaluationGallery() {
  if (outputState.loaded || outputState.loading) return;
  outputState.loading = true;
  try {
    const response = await fetch(STATIC_GALLERY_ENDPOINT);
    if (!response.ok) throw new Error(`Static gallery request failed with ${response.status}`);

    const payload = await response.json();
    outputState.all = payload.cases || [];
    outputState.families = payload.families || [];
    outputState.familyOrder = Object.fromEntries(outputState.families.map((family, index) => [family.id, index]));
    renderCaseFilterButtons(outputState.families);
    outputState.loaded = true;
    applyOutputFilters();
  } catch (error) {
    const grid = document.querySelector("[data-output-grid]");
    const count = document.querySelector("[data-output-count]");
    if (grid) {
      grid.innerHTML = `<div class="empty-gallery"><strong>Evaluation gallery unavailable</strong><p>${escapeHtml(error.message)}</p></div>`;
    }
    if (count) count.textContent = "Could not load evaluation cases";
  } finally {
    outputState.loading = false;
  }
}

function setupNavigation() {
  const menuButton = document.querySelector("[data-menu-toggle]");
  const mobileNav = document.querySelector("#mobile-navigation");
  const closeMobileMenu = () => {
    if (!menuButton || !mobileNav) return;
    menuButton.setAttribute("aria-expanded", "false");
    menuButton.setAttribute("aria-label", "Open navigation");
    menuButton.title = "Open navigation";
    menuButton.innerHTML = '<i data-lucide="menu" aria-hidden="true"></i>';
    mobileNav.hidden = true;
    refreshIcons(menuButton);
  };

  menuButton?.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") === "true";
    if (open) {
      closeMobileMenu();
      return;
    }
    menuButton.setAttribute("aria-expanded", "true");
    menuButton.setAttribute("aria-label", "Close navigation");
    menuButton.title = "Close navigation";
    menuButton.innerHTML = '<i data-lucide="x" aria-hidden="true"></i>';
    mobileNav.hidden = false;
    refreshIcons(menuButton);
  });
  const navLinks = [...document.querySelectorAll('.desktop-nav a[href^="#"], .mobile-nav a[href^="#"]')];
  const navIds = [...new Set(navLinks.map((link) => link.hash.slice(1)))];
  const navigationLinks = [...document.querySelectorAll('a[href^="#"]')]
    .filter((link) => navIds.includes(link.hash.slice(1)));
  const navSections = navIds.map((id) => document.getElementById(id)).filter(Boolean);
  const header = document.querySelector("[data-header]");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let navigationFrame = 0;
  let pendingNavigationId = "";
  let pendingNavigationUntil = 0;

  const navigationOffset = () => (header?.getBoundingClientRect().height || 0) + 18;
  const navigationTarget = (section) => {
    const explicitTarget = section?.querySelector("[data-navigation-target]");
    if (explicitTarget) return explicitTarget;
    const headingId = section?.getAttribute("aria-labelledby");
    return (headingId && document.getElementById(headingId)) || section;
  };
  const setActiveNavigation = (id) => {
    navLinks.forEach((link) => {
      const active = link.hash === `#${id}`;
      link.classList.toggle("is-active", active);
      if (active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  };
  const updateActiveNavigation = () => {
    navigationFrame = 0;
    const marker = navigationOffset() + 2;
    if (pendingNavigationId) {
      const pendingSection = document.getElementById(pendingNavigationId);
      const pendingTarget = navigationTarget(pendingSection);
      const reached = pendingTarget && Math.abs(pendingTarget.getBoundingClientRect().top - navigationOffset()) <= 3;
      if (!reached && performance.now() < pendingNavigationUntil) {
        setActiveNavigation(pendingNavigationId);
        return;
      }
      pendingNavigationId = "";
    }

    let activeId = "";
    navSections.forEach((section) => {
      if (navigationTarget(section).getBoundingClientRect().top <= marker) activeId = section.id;
    });
    const atPageEnd = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2;
    if (atPageEnd && navSections.length) activeId = navSections.at(-1).id;
    setActiveNavigation(activeId);
  };
  const scheduleActiveNavigation = () => {
    if (!navigationFrame) navigationFrame = window.requestAnimationFrame(updateActiveNavigation);
  };
  const scrollToNavigationSection = (id, { updateHash = true, behavior } = {}) => {
    const section = document.getElementById(id);
    const target = navigationTarget(section);
    if (!target) return;
    pendingNavigationId = id;
    pendingNavigationUntil = performance.now() + 1800;
    setActiveNavigation(id);
    if (updateHash && window.location.hash !== `#${id}`) history.pushState(null, "", `#${id}`);
    const top = Math.max(0, window.scrollY + target.getBoundingClientRect().top - navigationOffset());
    window.scrollTo({ top, behavior: behavior || (reducedMotion.matches ? "auto" : "smooth") });
    scheduleActiveNavigation();
  };

  navigationLinks.forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      closeMobileMenu();
      scrollToNavigationSection(link.hash.slice(1));
    });
  });
  const cancelPendingNavigation = () => {
    pendingNavigationId = "";
    scheduleActiveNavigation();
  };
  window.addEventListener("wheel", cancelPendingNavigation, { passive: true });
  window.addEventListener("touchstart", cancelPendingNavigation, { passive: true });
  window.addEventListener("hashchange", () => {
    const id = window.location.hash.slice(1);
    if (navIds.includes(id)) scrollToNavigationSection(id, { updateHash: false, behavior: "auto" });
  });

  const backToTop = document.querySelector("[data-back-to-top]");
  window.addEventListener(
    "scroll",
    () => {
      if (backToTop) backToTop.hidden = window.scrollY < 760;
      scheduleActiveNavigation();
    },
    { passive: true },
  );
  window.addEventListener("resize", scheduleActiveNavigation, { passive: true });
  backToTop?.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));

  const initialNavigationId = window.location.hash.slice(1);
  if (navIds.includes(initialNavigationId)) {
    window.requestAnimationFrame(() => scrollToNavigationSection(initialNavigationId, { updateHash: false, behavior: "auto" }));
  } else {
    scheduleActiveNavigation();
  }
}

function syncLeaderboardControls() {
  const search = document.querySelector("[data-leaderboard-search]");
  const interfaceSelect = document.querySelector("[data-leaderboard-interface]");
  if (search) search.value = leaderboardState.query;
  if (interfaceSelect) interfaceSelect.value = leaderboardState.interface;

  document.querySelectorAll("[data-leaderboard-group]").forEach((button) => {
    button.setAttribute("aria-pressed", String(leaderboardState.groups.has(button.dataset.leaderboardGroup)));
  });
}

function resetLeaderboardState() {
  leaderboardState.sortKey = "avg";
  leaderboardState.direction = "desc";
  leaderboardState.query = "";
  leaderboardState.interface = "all";
  leaderboardState.groups = new Set(metricGroups.map((group) => group.id));
}

function setupInteractions() {
  document.querySelector("[data-timeline-rail]")?.addEventListener("click", (event) => {
    const timelineButton = event.target.closest("[data-timeline-choice]");
    if (timelineButton) {
      setTimeline(timelineButton.dataset.timelineChoice);
      return;
    }

    const rail = event.currentTarget;
    const rect = rail.getBoundingClientRect();
    const choice = event.clientX >= rect.left + rect.width / 4 ? "public-100" : "release";
    setTimeline(choice);
  });

  document.querySelector(".leaderboard-table")?.addEventListener("click", (event) => {
    const sortButton = event.target.closest("[data-sort-key]");
    if (sortButton) {
      const key = sortButton.dataset.sortKey;
      if (leaderboardState.sortKey === key) {
        leaderboardState.direction = leaderboardState.direction === "desc" ? "asc" : "desc";
      } else {
        leaderboardState.sortKey = key;
        leaderboardState.direction = leaderboardPreferredDirection(key);
      }
      renderLeaderboard();
      return;
    }

  });

  document.querySelectorAll("[data-leaderboard-group]").forEach((button) => {
    button.addEventListener("click", () => {
      const id = button.dataset.leaderboardGroup;
      if (leaderboardState.groups.has(id)) leaderboardState.groups.delete(id);
      else leaderboardState.groups.add(id);
      if (!leaderboardState.groups.size) leaderboardState.groups.add("summary");
      ensureLeaderboardVisibleSort();
      syncLeaderboardControls();
      renderLeaderboard();
    });
  });

  document.querySelector("[data-leaderboard-search]")?.addEventListener("input", (event) => {
    leaderboardState.query = event.target.value;
    renderLeaderboardRows();
  });
  document.querySelector("[data-leaderboard-interface]")?.addEventListener("change", (event) => {
    leaderboardState.interface = event.target.value;
    renderLeaderboardRows();
  });
  document.querySelector("[data-leaderboard-reset]")?.addEventListener("click", () => {
    resetLeaderboardState();
    syncLeaderboardControls();
    renderLeaderboard();
  });

  document.querySelector("[data-case-search]")?.addEventListener("input", (event) => {
    outputState.query = event.target.value;
    outputState.visible = GALLERY_PAGE_SIZE;
    applyOutputFilters();
  });
  document.querySelector("[data-case-sort]")?.addEventListener("change", (event) => {
    outputState.sort = event.target.value;
    outputState.visible = GALLERY_PAGE_SIZE;
    applyOutputFilters();
  });
  document.querySelector("[data-case-filter-list]")?.addEventListener("click", (event) => {
    const button = event.target.closest("[data-case-filter]");
    if (!button) return;
    outputState.filter = button.dataset.caseFilter;
    outputState.visible = GALLERY_PAGE_SIZE;
    document.querySelectorAll("[data-case-filter]").forEach((peer) => {
      const active = peer === button;
      peer.classList.toggle("is-active", active);
      peer.setAttribute("aria-pressed", String(active));
    });
    applyOutputFilters();
  });
  document.querySelector("[data-output-load-more]")?.addEventListener("click", () => {
    outputState.visible += GALLERY_PAGE_SIZE;
    renderOutputs();
  });
  document.querySelector("[data-output-grid]")?.addEventListener("click", (event) => {
    const evidenceButton = event.target.closest("[data-output-evidence-index]");
    if (evidenceButton) {
      openOutputDialog(Number(evidenceButton.dataset.outputEvidenceIndex), "evidence");
      return;
    }
    const button = event.target.closest("[data-output-index]");
    if (button) openOutputDialog(Number(button.dataset.outputIndex));
  });
  document.querySelector("[data-output-result-rows]")?.addEventListener("click", (event) => {
    const row = event.target.closest("[data-output-result-model]");
    if (!row || !outputState.activeCase) return;
    const result = outputResultBySlug(outputState.activeCase, row.dataset.outputResultModel);
    if (result) selectOutputResult(outputState.activeCase, result, true);
  });
  document.querySelector("[data-output-result-rows]")?.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const row = event.target.closest("[data-output-result-model]");
    if (!row || !outputState.activeCase) return;
    event.preventDefault();
    const result = outputResultBySlug(outputState.activeCase, row.dataset.outputResultModel);
    if (result) selectOutputResult(outputState.activeCase, result, true);
  });

  const outputDialog = document.querySelector("[data-output-dialog]");
  document.querySelector("[data-close-output]")?.addEventListener("click", () => closeDialog(outputDialog));

  for (const dialog of [outputDialog]) {
    dialog?.addEventListener("click", (event) => {
      if (event.target === dialog) closeDialog(dialog);
    });
    dialog?.addEventListener("close", () => {
      document.body.classList.remove("dialog-open");
      dialog.querySelectorAll("video").forEach((video) => video.pause());
    });
  }
}

function setupContribFlipCards() {
  const cards = document.querySelectorAll(".contrib-card");
  cards.forEach((card) => {
    card.addEventListener("click", () => {
      card.classList.toggle("is-flipped");
    });
    card.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        card.classList.toggle("is-flipped");
      }
    });
  });
}

function setupAxesDisclosure() {
  const stack = document.querySelector("[data-axes-stack]");
  if (!stack) return;
  const buttons = [...stack.querySelectorAll("[data-axes-toggle]")];

  const setExpanded = (expanded) => {
    stack.classList.toggle("is-expanded", expanded);
    buttons.forEach((button) => {
      const label = expanded ? "Collapse all settings" : "Expand all settings";
      button.setAttribute("aria-expanded", String(expanded));
      button.setAttribute("aria-label", label);
      button.title = label;
    });
  };

  buttons.forEach((button) => {
    button.addEventListener("click", (event) => {
      setExpanded(!stack.classList.contains("is-expanded"));
      if (event.detail > 0) button.blur();
    });
  });
}

function setupSkillLibraryVideo() {
  const video = document.getElementById("skill-library-video");
  if (!video) return;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reducedMotion && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            video.play().catch(() => {});
            observer.disconnect();
          }
        }
      },
      { threshold: 0.45 }
    );
    observer.observe(video);
  }
  video.addEventListener("click", () => {
    video.currentTime = 0;
    video.play().catch(() => {});
  });
}

syncLeaderboardRankings();
renderLeaderboard();
syncTimeline();
syncLeaderboardControls();
setupHeroShowcase();
setupNavigation();
setupInteractions();
setupSkillLibraryVideo();
setupContribFlipCards();
setupAxesDisclosure();
refreshIcons();
setupBibtexCopy();
loadEvaluationGallery();
