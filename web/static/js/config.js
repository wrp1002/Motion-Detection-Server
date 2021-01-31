$(document).ready(function() {
    function PrettifyConfig() {
        const configText = $("#config-editor").val();
        const object = JSON.parse(configText);

        let str = JSON.stringify(object, undefined, 4);
        $('#config-editor').val(str);
    }

    function ValidateJSON(text) {
        try {
            JSON.parse(text);
            PrettifyConfig();
            return true;
        }
        catch(e) {
            return false;
        }
    }

    function ValidateConfig() {
        let configText = $("#config-editor").val();
        return ValidateJSON(configText);
    }

    function ReloadConfig() {
        $.ajax({
            url: "/api/config"
        })
        .done(function(res) {
            $("#config-editor").val(res);
            PrettifyConfig();
        });
    }

    $("#validate-btn").on('click', function() {
        if (ValidateConfig())
            flash("Valid!", "success");
        else
            flash("Invalid Formatting", "error");
    });

    $("#restore-btn").on('click', function() {
        $("#restoreModal").modal('show');
    })

    $("#restore-confirm-btn").on('click', function() {
        $("#restoreModal").modal('hide');

        $.ajax({
            url: location.location,
            method: "DELETE",
        })
        .done(function(res) {
            ReloadConfig();
            flash(res, 'success')
        });
    });

    $("#save-btn").on('click', function() {
        if (!ValidateConfig()) {
            flash('Invalid Formatting', 'error')
            return;
        }

        $.ajax({
            url: location.location,
            method: "POST",
            data: {
                "data": $("#config-editor").val()
            }
        })
        .done(function(res) {
            flash(res, 'success');
        })
    });

    PrettifyConfig();
})