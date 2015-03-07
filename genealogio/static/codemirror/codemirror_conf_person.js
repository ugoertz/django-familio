(function($) {
$(document).ready(function() {
    if ($("#id_comments").size()) {
        CodeMirror.commands.autocomplete = function(cm) {
            cm.showHint({hint: CodeMirror.hint.genrst });
        }
        var editor = new CodeMirror.fromTextArea($("#id_comments")[0],
            { width: "600px", height: "500px", lineWrapping: true, mode: 'rst',
            extraKeys: {"Ctrl-Space": "autocomplete"}, });

        // $("textarea#id_text + iframe").css("border", "1px solid rgb(204, 204, 204)");
    }
});
})(django.jQuery);
