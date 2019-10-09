$(document).ready(function() {
    if ($(".system-messages, .system-message").length) {
        $("#errormsg").html("Fehler anzeigen");
        $("#errormsg").css("display", "");
        $("#errormsg").click(function() {
            if ($("#errormsg").html() == "Fehler anzeigen") {
                $(".system-messages, .system-message").css("display", "block");
                $("#errormsg").html("Fehler ausblenden");
            } else {
                $(".system-messages, .system-message").css("display", "none");
                $("#errormsg").html("Fehler anzeigen");
            }
        });
    }
});


