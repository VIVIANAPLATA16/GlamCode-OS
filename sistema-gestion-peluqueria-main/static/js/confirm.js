document.addEventListener("click", function (event) {
  var target = event.target.closest(".js-confirm");
  if (!target) return;

  var msg = target.getAttribute("data-confirm") || "¿Estás seguro?";
  if (!confirm(msg)) {
    event.preventDefault();
  }
});

