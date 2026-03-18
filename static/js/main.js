document.addEventListener("DOMContentLoaded", function () {
  var btnMenu = document.getElementById("btn-menu-toggle");
  var sidebar = document.querySelector(".sidebar");

  if (btnMenu && sidebar) {
    btnMenu.addEventListener("click", function () {
      sidebar.classList.toggle("sidebar--open");
    });
  }

  document.querySelectorAll(".alert__close").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var alert = btn.closest(".alert");
      if (alert) {
        alert.remove();
      }
    });
  });
});

