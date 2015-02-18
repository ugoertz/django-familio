(function(mod) {
  if (typeof exports == "object" && typeof module == "object") // CommonJS
    mod(require("../../lib/codemirror"));
  else if (typeof define == "function" && define.amd) // AMD
    define(["../../lib/codemirror"], mod);
  else // Plain browser env
    mod(CodeMirror);
})(function(CodeMirror) {
  "use strict";

  CodeMirror.registerHelper("hint", "genrst", function(editor, callback, options) {
    var word = /:([a-z]+):`([A-Za-z0-9_\- \u00C0-\u017F]+)$/;
    var word1 = /[A-Za-z0-9_\-:$`\u00C0-\u017F]/;   // eat all characters from this regex
                                                    // to the right of cursor

    var cur = editor.getCursor(), curLine = editor.getLine(cur.line);
    var end = cur.ch, start;
    while (end < curLine.length && word1.test(curLine.charAt(end))) ++end;

    var matchResult = word.exec(curLine.slice(start, end));
    if (matchResult) {

      start = matchResult.index
      var role = matchResult[1];  // could check here whether this is a genealogio role
                                  // in order to save ajax calls
      Dajaxice.genealogio.autocomplete(function(result) {
        var list = [], seen = {};
        list = result;
        callback({list: list, from: CodeMirror.Pos(cur.line, start), to: CodeMirror.Pos(cur.line, end)});
      }, {q: matchResult[2], role: role});
    }
  });
  CodeMirror.hint.genrst.async = true
});

