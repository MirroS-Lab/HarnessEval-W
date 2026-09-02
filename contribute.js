const modes = {
  case: {
    guidance: "Complete the required fields before emailing your submission.",
    filename: "harnesseval-case-submission.json",
    emailUrl:
      "mailto:cwl24@mails.tsinghua.edu.cn?subject=%5BHarnessEval-W%5D%20Case%20%2F%20Taxonomy%20submission",
    discussUrl:
      "mailto:cwl24@mails.tsinghua.edu.cn?subject=%5BHarnessEval-W%5D%20Case%20%2F%20Taxonomy%20discussion",
    template: {
      schema_version: "harnesseval.case_submission.v1",
      kind: "case",
      case_id: "replace_with_case_id",
      title: "Concise case title",
      evaluation_question: "What observable behavior should this case evaluate?",
      taxonomy: {},
      world: {
        initial_observation: "assets/initial_observation.png",
      },
      action: {
        type: "physical_parameter_condition",
        text: "Describe the requested action and constraints.",
      },
      provenance: {
        author: "github-user",
        license: "Apache-2.0",
        redistribution_allowed: true,
      },
    },
  },
  skill: {
    guidance: "Define one evaluation question, its contract, implementation, and tests.",
    filename: "harnesseval-skill-submission.json",
    emailUrl:
      "mailto:cwl24@mails.tsinghua.edu.cn?subject=%5BHarnessEval-W%5D%20Skill%20submission",
    discussUrl:
      "mailto:cwl24@mails.tsinghua.edu.cn?subject=%5BHarnessEval-W%5D%20Skill%20discussion",
    template: {
      schema_version: "harnesseval.skill_submission.v1",
      kind: "skill",
      skill_id: "replace_with_skill_id",
      version: "0.1.0",
      question: "What single evaluation question does this skill answer?",
      applicable_families: ["physical_transition"],
      inputs: ["generated_video", "case.taxonomy", "case.action"],
      output: {
        score_range: [0, 1],
        evidence_required: true,
      },
      resources: {
        network: false,
        gpu_required: false,
        timeout_seconds: 300,
      },
      license: "Apache-2.0",
    },
  },
};

const workspace = document.querySelector(".submission-workspace");
const preview = document.querySelector("#template-preview");
const guidance = document.querySelector("#submission-guidance");
const submissionLink = document.querySelector("#submission-link");
const discussLink = document.querySelector("#discuss-link");
const downloadButton = document.querySelector("#download-template");
const status = document.querySelector("#download-status");
const modeButtons = [...document.querySelectorAll("[data-mode]")];
let activeMode = "case";
let statusTimer;

function refreshIcons(root = document) {
  if (window.lucide) window.lucide.createIcons({ attrs: { "stroke-width": 1.8 }, root });
}

function renderMode(mode) {
  const selected = modes[mode];
  if (!selected) return;

  activeMode = mode;
  workspace.dataset.mode = mode;
  preview.textContent = JSON.stringify(selected.template, null, 2);
  guidance.textContent = selected.guidance;
  submissionLink.href = selected.emailUrl;
  discussLink.href = selected.discussUrl;
  status.textContent = "";

  modeButtons.forEach((button) => {
    const isSelected = button.dataset.mode === mode;
    button.setAttribute("aria-selected", String(isSelected));
    button.tabIndex = isSelected ? 0 : -1;
  });
  refreshIcons();
}

function openBuilder(mode) {
  renderMode(mode);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelector("#submission-template").scrollIntoView({
    behavior: reduceMotion ? "auto" : "smooth",
    block: "start",
  });
}

function downloadTemplate() {
  const selected = modes[activeMode];
  const blob = new Blob([`${JSON.stringify(selected.template, null, 2)}\n`], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = selected.filename;
  link.click();
  window.setTimeout(() => URL.revokeObjectURL(url), 0);

  window.clearTimeout(statusTimer);
  status.textContent = `${selected.filename} downloaded.`;
  statusTimer = window.setTimeout(() => {
    status.textContent = "";
  }, 4000);
}

function setupMenu() {
  const button = document.querySelector("[data-menu-toggle]");
  const menu = document.querySelector("#mobile-navigation");
  if (!button || !menu) return;

  const setOpen = (open) => {
    button.setAttribute("aria-expanded", String(open));
    button.setAttribute("aria-label", open ? "Close navigation" : "Open navigation");
    button.title = open ? "Close navigation" : "Open navigation";
    button.innerHTML = `<i data-lucide="${open ? "x" : "menu"}" aria-hidden="true"></i>`;
    menu.hidden = !open;
    refreshIcons(button);
  };

  button.addEventListener("click", () => {
    setOpen(button.getAttribute("aria-expanded") !== "true");
  });
  menu.addEventListener("click", (event) => {
    if (event.target.closest("a")) setOpen(false);
  });
}

document.querySelectorAll("[data-open-entry]").forEach((button) => {
  button.addEventListener("click", () => openBuilder(button.dataset.openEntry));
});

modeButtons.forEach((button, index) => {
  button.addEventListener("click", () => renderMode(button.dataset.mode));
  button.addEventListener("keydown", (event) => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const direction = event.key === "ArrowRight" ? 1 : -1;
    const next = modeButtons[(index + direction + modeButtons.length) % modeButtons.length];
    renderMode(next.dataset.mode);
    next.focus();
  });
});

downloadButton.addEventListener("click", downloadTemplate);
setupMenu();
renderMode(activeMode);
refreshIcons();
window.addEventListener("load", refreshIcons);
