const reportList = document.querySelector("#report-list");
const searchInput = document.querySelector("#search-input");
const form = document.querySelector("#report-form");
const formMessage = document.querySelector("#form-message");
const loadError = document.querySelector("#load-error");
const filterButtons = [...document.querySelectorAll(".filter-tab")];
let reports = [];
let activeFilter = "all";

function setMessage(element, message, type) {
  element.className = `message ${type || ""}`.trim();
  element.textContent = message;
}

function safeDate(value) {
  if (!value) return "Date not specified";
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? "Date not specified"
    : new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(date);
}

function createReportCard(report) {
  const article = document.createElement("article");
  article.className = "report-card";

  const top = document.createElement("div");
  top.className = "report-card-top";
  const title = document.createElement("h3");
  title.textContent = report.title;
  const badge = document.createElement("span");
  badge.className = `report-badge ${report.report_type}`;
  badge.textContent = report.report_type;
  top.append(title, badge);

  const details = document.createElement("div");
  details.className = "report-details";
  const category = document.createElement("span");
  category.textContent = report.category;
  const location = document.createElement("span");
  location.className = "detail-location";
  location.textContent = report.location;
  details.append(category, location);

  const description = document.createElement("p");
  description.className = "report-description";
  description.textContent = report.description;
  const date = document.createElement("div");
  date.className = "report-date";
  date.textContent = safeDate(report.reported_at);
  article.append(top, details, description, date);
  return article;
}

function renderReports() {
  const search = searchInput.value.trim().toLocaleLowerCase();
  const visibleReports = reports.filter((report) => {
    const matchesFilter = activeFilter === "all" || report.report_type === activeFilter;
    const searchableText = [report.title, report.category, report.location, report.description]
      .join(" ")
      .toLocaleLowerCase();
    return matchesFilter && searchableText.includes(search);
  });

  reportList.replaceChildren();
  if (!visibleReports.length) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    const mark = document.createElement("span");
    mark.className = "empty-state-mark";
    mark.textContent = search || activeFilter !== "all" ? "..." : "+";
    const title = document.createElement("h3");
    title.textContent = search || activeFilter !== "all" ? "No reports match just yet" : "Be the first to share";
    const text = document.createElement("p");
    text.textContent = search || activeFilter !== "all"
      ? "Try another search or filter, or check back soon."
      : "Your report could be the little detail that helps something find its way home.";
    empty.append(mark, title, text);
    reportList.append(empty);
  } else {
    reportList.append(...visibleReports.map(createReportCard));
  }

  document.querySelector("#total-count").textContent = reports.length;
  document.querySelector("#lost-count").textContent = reports.filter((item) => item.report_type === "lost").length;
  document.querySelector("#found-count").textContent = reports.filter((item) => item.report_type === "found").length;
}

async function loadReports() {
  loadError.hidden = true;
  try {
    const response = await fetch("/api/reports");
    if (!response.ok) throw new Error("Could not load community reports.");
    reports = await response.json();
    renderReports();
  } catch (error) {
    loadError.textContent = error.message || "Could not load community reports.";
    loadError.hidden = false;
  }
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    filterButtons.forEach((tab) => tab.classList.toggle("active", tab === button));
    renderReports();
  });
});

document.querySelectorAll(".type-option").forEach((option) => {
  option.addEventListener("change", () => {
    document.querySelectorAll(".type-option").forEach((item) => item.classList.remove("selected"));
    option.classList.add("selected");
  });
});

searchInput.addEventListener("input", renderReports);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = form.querySelector(".submit-button");
  const values = new FormData(form);
  const payload = {
    title: values.get("title").trim(),
    description: values.get("description").trim(),
    category: values.get("category"),
    location: values.get("location").trim(),
    report_type: values.get("report_type"),
    image_path: values.get("image_path").trim() || null,
    reported_at: values.get("reported_at") ? new Date(values.get("reported_at")).toISOString() : null,
  };

  submitButton.disabled = true;
  setMessage(formMessage, "Sharing your report...", "");
  try {
    const response = await fetch("/api/reports", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();
    if (!response.ok) {
      const detail = Array.isArray(result.detail)
        ? result.detail.map((issue) => issue.msg).join(" ")
        : result.detail;
      throw new Error(detail || "Your report could not be saved.");
    }

    form.reset();
    document.querySelector('.type-option[data-type="lost"]').classList.add("selected");
    document.querySelector('.type-option[data-type="found"]').classList.remove("selected");
    const summary = result.matches_found
      ? `Your report is live. We found ${result.matches_found} possible ${result.matches_found === 1 ? "match" : "matches"} in the community board.`
      : "Your report is live. We will show possible matches as similar reports are shared.";
    setMessage(formMessage, summary, "success-message");
    if (result.matches_found) {
      const match = result.matches[0];
      const matchNotice = document.createElement("div");
      matchNotice.className = "match-message";
      const heading = document.createElement("strong");
      heading.textContent = `Possible match (${Math.round(match.score * 100)}% similarity)`;
      const detail = document.createElement("span");
      const matchedReport = reports.find((item) => item.item_id === match.item_id);
      detail.textContent = matchedReport
        ? `${matchedReport.title} — ${matchedReport.location}`
        : match.reason;
      matchNotice.append(heading, detail);
      formMessage.append(matchNotice);
    }
    activeFilter = "all";
    filterButtons.forEach((tab) => tab.classList.toggle("active", tab.dataset.filter === "all"));
    searchInput.value = "";
    await loadReports();
  } catch (error) {
    setMessage(formMessage, error.message || "Your report could not be saved.", "error-message");
  } finally {
    submitButton.disabled = false;
  }
});

loadReports();
