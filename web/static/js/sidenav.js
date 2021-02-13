$(document).ready(function() {
    $("#sidebar").on('mouseleave', function() {
        $(".dropdown-toggle").attr("aria-expanded", false);
        $(".collapse").collapse('hide');
        setTimeout(function() {$(".collapse").collapse('hide');}, 400);
    })


    $("#restart-btn").on('click', function() {
        $.ajax({
            url: "/api/restart"
        })
        .done(function() {
            flash("Restarting")
            location.reload();
        });
    });

    $("#shutdown-btn").on('click', function() {
        flash("Shutting Down...")
        $.ajax({
            url: "/api/shutdown"
        });
    });
});
