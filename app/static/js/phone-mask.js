(function () {
  function formatPhone(raw) {
    let digits = (raw || "").replace(/\D/g, "");
    if (digits.startsWith("8")) digits = "7" + digits.slice(1);
    if (digits.length === 10) digits = "7" + digits;
    if (!digits.startsWith("7")) digits = "7" + digits;

    const p = digits.slice(0, 11);
    const a = p.slice(1, 4);
    const b = p.slice(4, 7);
    const c = p.slice(7, 9);
    const d = p.slice(9, 11);

    let out = "+7";
    if (a) out += " (" + a;
    if (a.length === 3) out += ")";
    if (b) out += " " + b;
    if (c) out += "-" + c;
    if (d) out += "-" + d;
    return out;
  }

  document.querySelectorAll("[data-phone-mask]").forEach((input) => {
    input.addEventListener("input", () => {
      input.value = formatPhone(input.value);
    });
    input.addEventListener("focus", () => {
      if (!input.value) input.value = "+7";
    });
  });
})();