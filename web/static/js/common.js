function flash(message, category="message") {
    let msg = "<li class=" + category + ">";
    if (category == "success")
        msg += '<i class="fas fa-check-circle"></i>';
    else if (category == "error")
        msg += '<i class="fas fa-exclamation-circle"></i>';
    else
        msg += '<i class="fas fa-info-circle"></i>';
    msg += " " + message;
    msg += "</li>"
    msg = $(msg);
    msg.on('click', function() {
        $(this).fadeOut(500, function() {
            $(this).remove();
        });
    });

    setTimeout(function() {
        $(msg).fadeOut(1000, function() {
            $(this).remove();
        });
    }, 5000);

    $("#flash-messages").append(msg);
}

$(document).ready(function() {
    $(".flashes li").on('click', function() {
        $(this).fadeOut('fast', function() {
            $(this).remove();
        });
    });
});
