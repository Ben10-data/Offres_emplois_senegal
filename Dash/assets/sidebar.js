document.addEventListener("click", function (e) {

    if (
        e.target.closest("#nav-eda") ||
        e.target.closest("#nav-matching") ||
        e.target.closest("#nav-competences")
    ) {

        const offcanvas = document.getElementById("offcanvas-sidebar");

        if (offcanvas && offcanvas.classList.contains("show")) {

            bootstrap.Offcanvas.getInstance(offcanvas).hide();

        }
    }
});