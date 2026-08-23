(function () {
  if (window.__netieHireBand) return;
  window.__netieHireBand = true;

  var css = [
    "#netie-hire-band{position:fixed;left:0;right:0;bottom:0;z-index:2147483000;",
    "display:flex;justify-content:center;padding:0 0.75rem 0.75rem;pointer-events:none;",
    "font:15px/1.35 ui-sans-serif,system-ui,-apple-system,sans-serif;}",
    "#netie-hire-band .n-band{pointer-events:auto;width:100%;max-width:36rem;",
    "display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:0.55rem 0.75rem;",
    "padding:0.7rem 0.85rem;border:1px solid #2a3c4a;border-radius:14px;",
    "background:rgba(7,12,18,0.94);color:#e8f0f4;box-shadow:0 10px 40px rgba(0,0,0,0.35);}",
    "#netie-hire-band p{margin:0;color:#9bb0c0;font-size:0.82rem;}",
    "#netie-hire-band a{color:#4fdec6;font-weight:700;text-decoration:none;}",
    "#netie-hire-band a:hover{text-decoration:underline;}",
    "#netie-hire-band a.primary{display:inline-flex;align-items:center;min-height:36px;",
    "padding:0 0.75rem;border-radius:8px;background:#4fdec6;color:#03130f;}",
    "body.netie-hire-pad{padding-bottom:5.5rem;}"
  ].join("");

  function mount() {
    if (document.getElementById("netie-hire-band")) return;
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);
    document.body.classList.add("netie-hire-pad");
    var wrap = document.createElement("div");
    wrap.id = "netie-hire-band";
    wrap.setAttribute("role", "navigation");
    wrap.setAttribute("aria-label", "Hire and demos");
    wrap.innerHTML =
      '<div class="n-band">' +
      "<p>Hire us for your work.</p>" +
      '<a class="primary" href="/hire/">Open hire</a>' +
      '<a href="/projects/">See demos</a>' +
      '<a href="/aim/">AIM</a>' +
      '<a href="/asa/">ASA</a>' +
      '<a href="/suite/">Suite</a>' +
      "</div>";
    document.body.appendChild(wrap);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
  setTimeout(mount, 600);
})();
