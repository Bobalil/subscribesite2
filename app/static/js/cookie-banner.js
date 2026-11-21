(function () {
  const KEY = "cookie_consent";
  if (document.cookie.split(";").some(c => c.trim().startsWith(KEY + "="))) return;

  const banner = document.createElement("div");
  banner.style.cssText = "position:fixed;bottom:0;left:0;right:0;background:#111;color:#fff;padding:12px;display:flex;gap:12px;align-items:center;z-index:9999;font-size:14px";
  banner.innerHTML = `
    <span>Мы используем cookie для работы сайта. Подробнее — <a href="/legal/cookies" style="color:#8cf" target="_blank">здесь</a>.</span>
    <button id="cookie-accept" style="margin-left:auto;padding:6px 12px;cursor:pointer">Принять</button>
  `;
  document.body.appendChild(banner);
  document.getElementById("cookie-accept").addEventListener("click", async () => {
    await fetch("/legal/accept-cookies", { method: "POST" });
    banner.remove();
  });
})();