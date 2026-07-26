document.addEventListener("DOMContentLoaded", function () {

    document.addEventListener("click", function (e) {

        const link = e.target.closest(
            "#nav-eda, #nav-matching, #nav-competences"
        );

        if (!link) return;

        const offcanvas = document.getElementById("offcanvas-sidebar");

        if (!offcanvas) return;

        const bsOffcanvas = bootstrap.Offcanvas.getInstance(offcanvas);

        if (bsOffcanvas) {
            bsOffcanvas.hide();
        }

    });

});