(function () {
  "use strict";
  var btn = document.getElementById("whatIfBtn");
  var input = document.getElementById("whatIfSkills");
  var result = document.getElementById("whatIfResult");
  if (!btn || !input || !result) return;

  function esc(v) { return String(v == null ? "" : v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"); }
  function profile() {
    try { return JSON.parse(localStorage.getItem("pathnotes_onboarding") || "{}"); }
    catch (e) { return {}; }
  }

  btn.addEventListener("click", function () {
    var skills = input.value.split(",").map(function (x) { return x.trim(); }).filter(Boolean);
    if (!skills.length) { result.textContent = "Enter at least one skill."; return; }
    btn.disabled = true;
    btn.textContent = "Calculating...";
    fetch("/api/what-if", { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({profile:profile(), addSkills:skills}) })
      .then(function (r) { if (!r.ok) throw new Error("API error"); return r.json(); })
      .then(function (d) {
        var delta = Number(d.improvement || 0);
        var sign = delta > 0 ? "+" : "";
        var explanation = (d.explanation || []).map(function (f) { return "<li>" + esc(f.factor) + ": " + f.value + "%</li>"; }).join("");
        result.innerHTML = "<div style=\"display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;\">" +
          "<div><small>Before</small><strong style=\"display:block;font-size:26px;\">" + d.before.readiness + "%</strong></div>" +
          "<div><small>After learning</small><strong style=\"display:block;font-size:26px;\">" + d.after.readiness + "%</strong></div>" +
          "<div><small>Change</small><strong style=\"display:block;font-size:26px;\">" + sign + delta + "%</strong></div></div>" +
          "<p style=\"margin-top:14px;\"><b>Target role:</b> " + esc(d.after.role) + "</p>" +
          "<p><b>Still missing:</b> " + esc((d.after.missing || []).slice(0,5).join(", ") || "No major listed gap") + "</p>" +
          "<details style=\"margin-top:10px;\"><summary>Why did it change?</summary><ul>" + explanation + "</ul></details>";
      })
      .catch(function () { result.textContent = "Could not reach the Python backend. Make sure Flask is running."; })
      .finally(function () { btn.disabled = false; btn.textContent = "Simulate"; });
  });
})();
