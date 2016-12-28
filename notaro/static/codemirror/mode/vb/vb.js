'use strict';(function(e){"object"==typeof exports&&"object"==typeof module?e(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],e):e(CodeMirror)})(function(e){e.defineMode("vb",function(g,u){function d(a){return new RegExp("^(("+a.join(")|(")+"))\\b","i")}function f(a,b){if(a.eatSpace())return null;if("'"===a.peek())return a.skipToEnd(),"comment";if(a.match(/^((&H)|(&O))?[0-9\.a-f]/i,!1)){var c=!1;a.match(/^\d*\.\d+F?/i)?c=!0:a.match(/^\d+\.\d*F?/)?
c=!0:a.match(/^\.\d+F?/)&&(c=!0);if(c)return a.eat(/J/i),"number";c=!1;a.match(/^&H[0-9a-f]+/i)?c=!0:a.match(/^&O[0-7]+/i)?c=!0:a.match(/^[1-9]\d*F?/)?(a.eat(/J/i),c=!0):a.match(/^0(?![\dx])/i)&&(c=!0);if(c)return a.eat(/L/i),"number"}if(a.match('"'))return b.tokenize=v(a.current()),b.tokenize(a,b);if(a.match(w)||a.match(x))return null;if(a.match(y)||a.match(z)||a.match(A))return"operator";if(a.match(B))return null;if(a.match(C))return b.currentIndent++,b.doInCurrentLine=!0,"keyword";if(a.match(D))return b.doInCurrentLine?
b.doInCurrentLine=!1:b.currentIndent++,"keyword";if(a.match(h))return"keyword";if(a.match(k))return b.currentIndent--,b.currentIndent--,"keyword";if(a.match(l))return b.currentIndent--,"keyword";if(a.match(E)||a.match(F))return"keyword";if(a.match(G))return"variable";a.next();return"error"}function v(a){var b=1==a.length;return function(c,d){for(;!c.eol();){c.eatWhile(/[^'"]/);if(c.match(a))return d.tokenize=f,"string";c.eat(/['"]/)}if(b){if(u.singleLineStringErrors)return"error";d.tokenize=f}return"string"}}
var z=/^[\+\-\*/%&\\|\^~<>!]/,B=/^[\(\)\[\]\{\}@,:`=;\.]/,y=/^((==)|(<>)|(<=)|(>=)|(<>)|(<<)|(>>)|(\/\/)|(\*\*))/,x=/^((\+=)|(\-=)|(\*=)|(%=)|(\/=)|(&=)|(\|=)|(\^=))/,w=/^((\/\/=)|(>>=)|(<<=)|(\*\*=))/,G=/^[_A-Za-z][_A-Za-z0-9]*/,m="class module sub enum select while if function get set property try".split(" "),n=["else","elseif","case","catch"],p=["next","loop"],q=["and","or","not","xor","in"],A=d(q),r="as dim break continue optional then until goto byval byref new handles property return const private protected friend public shared static true false".split(" "),
t="integer string double decimal boolean short char float single".split(" "),F=d(r),E=d(t),D=d(m),h=d(n),l=d(p),k=d(["end"]),C=d(["do"]);e.registerHelper("hintWords","vb",m.concat(n).concat(p).concat(q).concat(r).concat(t));return{electricChars:"dDpPtTfFeE ",startState:function(){return{tokenize:f,lastToken:null,currentIndent:0,nextLineIndent:0,doInCurrentLine:!1}},token:function(a,b){a.sol()&&(b.currentIndent+=b.nextLineIndent,b.nextLineIndent=0,b.doInCurrentLine=0);var c;c=b.tokenize(a,b);var d=
a.current();if("."===d)c=b.tokenize(a,b),a.current(),c="variable"===c?"variable":"error";else{var e="[({".indexOf(d);-1!==e&&b.currentIndent++;e="])}".indexOf(d);-1!==e&&b.currentIndent--}b.lastToken={style:c,content:a.current()};return c},indent:function(a,b){b=b.replace(/^\s+|\s+$/g,"");return b.match(l)||b.match(k)||b.match(h)?g.indentUnit*(a.currentIndent-1):0>a.currentIndent?0:a.currentIndent*g.indentUnit},lineComment:"'"}});e.defineMIME("text/x-vb","vb")});
