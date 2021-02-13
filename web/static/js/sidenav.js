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
            flash("Restarting");
            setTimeout(function(){location.reload();}, 1000);
        });
    });

    $("#shutdown-btn").on('click', function() {
        flash("Shutting Down...")
        $.ajax({
            url: "/api/shutdown"
        });
    });

    $("#check-updates-btn").on('click', function() {
        $("#updates-loading").attr('hidden', false);
        $("#latest-version").attr('hidden', true);
        $("#current-version").attr('hidden', true);

        $("#updatesModal").modal('show');
        $.ajax({
            url: "/api/versions"
        })
        .done(function(res) {
            versions = JSON.parse(res);
            $("#current-version").text("Current Version: " + versions.current);
            $("#latest-version").text("Latest Version: " + versions.latest);
            $("#latest-version").attr('hidden', false);
            $("#current-version").attr('hidden', false);
            $("#updates-loading").attr('hidden', true);
        })
    });
});
