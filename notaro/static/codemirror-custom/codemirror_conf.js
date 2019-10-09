(function($) {
$(document).ready(function() {
    if ($("#id_text").length) {
        CodeMirror.commands.autocomplete = function(cm) {
            cm.showHint({hint: CodeMirror.hint.genrst });
        }
        var editor = new CodeMirror.fromTextArea($("#id_text")[0],
            { width: "600px", height: "500px", lineWrapping: true, mode: 'rst',
            extraKeys: {"Ctrl-Space": "autocomplete"}, });

        window.editor = editor;
    }
});
})(django.jQuery);
