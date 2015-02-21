$(document).ready(function() {
    if ($(".system-message").size()) {
        $("#errormsg").html("Fehler anzeigen");
        $("#errormsg").css("display", "");
        $("#errormsg").click(function() {
            if ($("#errormsg").html() == "Fehler anzeigen") {
                $(".system-message").css("display", "block");
                $("#errormsg").html("Fehler ausblenden");
            } else {
                $(".system-message").css("display", "none");
                $("#errormsg").html("Fehler anzeigen");
            }
        });
    }
});


