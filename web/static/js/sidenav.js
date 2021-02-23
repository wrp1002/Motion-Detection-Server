$(document).ready(function() {
    let pingCount = 0;

    // Wait for server to shutdown
    function PingServerForShutdown() {
        $.ajax({
            url: "/api/ping",
            timeout: 1000
        })
        .fail(function() {
            pingCount = 100;
            flash("Server shutdown!", "success")
        })
        .always(function() {
            pingCount++;
            if (pingCount < 10)
                PingServerForShutdown();
        })
    }

    // Collapse sidebar
    $("#sidebar").on('mouseleave', function() {
        $(".dropdown-toggle").attr("aria-expanded", false);
        $(".collapse").collapse('hide');
        setTimeout(function() {$(".collapse").collapse('hide');}, 400);
    })

    // Restart
    $("#restart-btn").on('click', function() {
        $.ajax({
            url: "/api/restart"
        })
        .done(function(res) {
            flash(res);
            setTimeout(function(){location.reload();}, 1000);
        })
        .fail(function(res) {
            flash(res.responseText, "error");
        })
    });

    // Shutdown 
    $("#shutdown-btn").on('click', function() {
        console.log('shutdown click')
        console.log($("#shutdownModal"));
        $("#shutdownModal").modal('show');
    });

    $("#shutdown-modal-btn").on('click', function() {
        $.ajax({
            url: "/api/shutdown"
        })
        .done(function(res) {
            flash(res);
            pingCount = 0;
            PingServerForShutdown();
        })
        .fail(function(res) {
            flash(res.responseText, "error");
        })
        .always(function() {
            $("#shutdownModal").modal('hide');
        })
    });

    // Update
    $("#update-btn").on('click', function() {
        $.ajax({
            url: "/api/update_server"
        })
        .done(function(res) {
            flash(res);
        })
        .fail(function(res) {
            flash(res.responseText, "error");
        })
        .always(function() {
            $("#updatesModal").modal('hide');
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

});
