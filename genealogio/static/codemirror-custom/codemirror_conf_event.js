(function($) {
$(document).ready(function() {
    if ($("#id_description").length) {
        CodeMirror.commands.autocomplete = function(cm) {
            cm.showHint({hint: CodeMirror.hint.genrst });
        }
        var editor = new CodeMirror.fromTextArea($("#id_description")[0],
            { width: "600px", height: "500px", lineWrapping: true, mode: 'rst',
            extraKeys: {"Ctrl-Space": "autocomplete"}, });

        window.editor = editor;
    }
});
})(django.jQuery);
