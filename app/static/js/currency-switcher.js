(function () {
  const KEY = "preferred_currency";
  const current = localStorage.getItem(KEY) || "RUB";
  
  // Устанавливаем текущую валюту в селект
  document.querySelectorAll("[data-currency-switcher]").forEach((el) => {
    el.value = current;
    
    // При смене валюты
    el.addEventListener("change", async (e) => {
      const to = e.target.value;
      localStorage.setItem(KEY, to);
      updatePrices(to);
    });
  });

  // Функция обновления цен
  async function updatePrices(toCurrency) {
    try {
      // Получаем актуальный курс
      const res = await fetch('/currency/rate');
      const data = await res.json();
      const rate = data.USD_RUB;

      document.querySelectorAll("[data-price-rub]").forEach((node) => {
        const rub = parseFloat(node.dataset.priceRub);
        if (toCurrency === "USD") {
          node.textContent = "$" + (rub / rate).toFixed(2);
        } else {
          node.textContent = rub.toFixed(2) + " ₽";
        }
      });
    } catch (e) {
      console.error("Ошибка загрузки курса", e);
    }
  }

  // Применяем валюту при загрузке страницы
  if (current === "USD") {
    updatePrices("USD");
  }
})();
