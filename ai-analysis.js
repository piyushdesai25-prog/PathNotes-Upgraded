(function () {
  "use strict";
  var API = "http://127.0.0.1:5000/api/analyze-profile";
  var status = document.getElementById("aiStatus");
  if (!status) return;

  function escapeHtml(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function getProfile() {
    try { return JSON.parse(localStorage.getItem("pathnotes_onboarding") || "{}"); }
    catch (e) { return {}; }
  }

  function render(result) {
    var primary = result.primary_role || {};
    document.getElementById("aiStatus").textContent = "AI engine connected • " + result.dataset.career_rows + " career-skill records • " + result.dataset.student_profiles + " demo profiles";
    document.getElementById("aiPrimaryRole").textContent = primary.role || "Not enough data";
    document.getElementById("aiReadiness").textContent = (primary.readiness || 0) + "%";
    document.getElementById("aiClusterLabel").textContent = (result.cluster || {}).label || "—";
    document.getElementById("aiClusterText").textContent = "Cluster " + ((result.cluster || {}).cluster || "—") + " based on the profile feature vector.";
    var anomaly = result.anomaly || {};
    document.getElementById("aiAnomalyLabel").textContent = anomaly.is_anomaly ? "Unusual profile" : "Normal profile";
    document.getElementById("aiAnomalyText").textContent = anomaly.interpretation || "No anomaly result.";

    var factors = primary.explanation || [];
    document.getElementById("aiExplanation").innerHTML = factors.map(function (f) {
      return '<div class="ai-factor-line"><span>' + escapeHtml(f.factor) + '</span><b>' + f.value + '%</b></div>' +
        '<div class="ai-factor-bar"><div class="ai-factor-fill" style="width:' + Math.max(0, Math.min(100, f.value)) + '%"></div></div>';
    }).join("");

    document.getElementById("aiFactors").innerHTML = factors.map(function (f) {
      return '<div><div class="ai-factor-line"><span>' + escapeHtml(f.factor) + ' <small>(' + f.weight + '% weight)</small></span><b>' + f.value + '%</b></div>' +
        '<div class="ai-factor-bar"><div class="ai-factor-fill" style="width:' + Math.max(0, Math.min(100, f.value)) + '%"></div></div></div>';
    }).join("");

    document.getElementById("aiMissingSkills").innerHTML = (primary.missing || []).slice(0, 6).map(function (s) {
      return '<span class="ai-tag">Missing: ' + escapeHtml(s) + '</span>';
    }).join("") || '<span class="ai-tag">No major required skill gap</span>';

    document.getElementById("aiRecommendations").innerHTML = '<b>Model recommendations</b>' +
      (result.recommendations || []).map(function (r) { return '<div class="ai-rec">• ' + escapeHtml(r) + '</div>'; }).join("");
  }

  fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(getProfile())
  }).then(function (response) {
    if (!response.ok) throw new Error("API returned " + response.status);
    return response.json();
  }).then(render).catch(function () {
    status.innerHTML = "AI engine is offline. Start <b>run_backend.bat</b> (Windows) or <b>./run_backend.sh</b> (Linux/macOS), then refresh this dashboard.";
    document.getElementById("aiPrimaryRole").textContent = "Backend not running";
  });
})();
