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
        .done(function(res) {
            flash(res);
            setTimeout(function(){location.reload();}, 1000);
        });
    });

    $("#shutdown-btn").on('click', function() {
        $.ajax({
            url: "/api/shutdown"
        })
        .done(function(res) {
            flash(res);
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
            let updated = (versions.current == versions.latest);
            $("#current-version").text("Current Version: " + versions.current);
            $("#latest-version").text("Latest Version: " + versions.latest);
            $("#latest-version").attr('hidden', false);
            $("#current-version").attr('hidden', false);
            $("#updates-loading").attr('hidden', true);
            $("#update-btn").attr('disabled', updated);
        })
    });

    $("#update-btn").on('click', function() {
        $.ajax({
            url: "/api/update_server",
            method: "POST"
        })
        .done(function(res) {
            flash(res);
        })
        .fail(function() {
            flash("Error with request", "error");
        })
        .always(function() {
            $("#updatesModal").modal('hide');
        });
    });
});
