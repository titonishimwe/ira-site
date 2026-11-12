// Store name and WhatsApp number are edited in the Django admin (Site settings).
const WHATSAPP_NUMBER = document.body.dataset.whatsapp;
const STORE_NAME = document.body.dataset.store;

function waLink(text) {
  return "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + encodeURIComponent(text);
}

// General "chat" buttons (nav, footer, floating button)
document.querySelectorAll(".js-chat").forEach(function (el) {
  el.href = waLink("Hello " + STORE_NAME + ", I would like to ask about your products.");
  el.target = "_blank";
  el.rel = "noopener";
});

// Fire-and-forget: WhatsApp must open even if the backend is unreachable.
function logOrder(productId, size) {
  fetch(document.body.dataset.orderUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-CSRFToken": document.body.dataset.csrf },
    body: JSON.stringify({ product: productId, size: size }),
    keepalive: true
  }).catch(function () {});
}

// Order buttons
document.querySelectorAll(".js-order").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var body = btn.closest(".product-body");
    var select = body.querySelector(".size-select");
    var size = "";
    if (select) {
      if (!select.value) {
        select.classList.add("is-invalid");
        select.focus();
        return;
      }
      select.classList.remove("is-invalid");
      size = select.value;
    }
    var msg = "Hello " + STORE_NAME + ", I would like to order:\n" +
      "- " + btn.dataset.name + (size ? " (size " + size + ")" : "") +
      " - " + btn.dataset.price + "\nQuantity: 1";
    logOrder(btn.dataset.id, size);
    window.open(waLink(msg), "_blank", "noopener");
  });
});

// Category filter + search
var grid = document.getElementById("grid");
if (grid) {
  var cols = Array.prototype.slice.call(grid.querySelectorAll(".product-col"));
  var chips = document.querySelectorAll(".chip");
  var search = document.getElementById("search");
  var empty = document.getElementById("empty");
  var current = "all";

  function apply() {
    var q = search.value.trim().toLowerCase();
    var shown = 0;
    cols.forEach(function (c) {
      var ok = (current === "all" || c.dataset.category === current) &&
               (!q || c.dataset.name.indexOf(q) !== -1);
      c.classList.toggle("d-none", !ok);
      if (ok) shown++;
    });
    empty.classList.toggle("d-none", shown !== 0);
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      chips.forEach(function (c) { c.classList.remove("active"); });
      chip.classList.add("active");
      current = chip.dataset.filter;
      apply();
    });
  });
  search.addEventListener("input", apply);
}
