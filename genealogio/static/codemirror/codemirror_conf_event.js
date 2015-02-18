(function($) {
$(document).ready(function() {
    CodeMirror.commands.autocomplete = function(cm) {
        cm.showHint({hint: CodeMirror.hint.genrst });
    }
    var editor = new CodeMirror.fromTextArea($("#id_description")[0],
        { width: "600px", height: "500px", lineWrapping: true, mode: 'rst',
          extraKeys: {"Ctrl-Space": "autocomplete"}, });

    // $("textarea#id_text + iframe").css("border", "1px solid rgb(204, 204, 204)");
});
})(django.jQuery);
