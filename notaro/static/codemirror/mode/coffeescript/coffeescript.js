'use strict';(function(e){"object"==typeof exports&&"object"==typeof module?e(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],e):e(CodeMirror)})(function(e){e.defineMode("coffeescript",function(e,t){function k(a){return new RegExp("^(("+a.join(")|(")+"))\\b")}function h(a,b){if(a.sol()){null===b.scope.align&&(b.scope.align=!1);var c=b.scope.offset;if(a.eatSpace())return a=a.indentation(),a>c&&"coffee"==b.scope.type?"indent":a<c?"dedent":null;
0<c&&m(a,b)}if(a.eatSpace())return null;c=a.peek();if(a.match("####"))return a.skipToEnd(),"comment";if(a.match("###"))return b.tokenize=u,b.tokenize(a,b);if("#"===c)return a.skipToEnd(),"comment";if(a.match(/^-?[0-9\.]/,!1)){c=!1;a.match(/^-?\d*\.\d+(e[\+\-]?\d+)?/i)&&(c=!0);a.match(/^-?\d+\.\d*/)&&(c=!0);a.match(/^-?\.\d+/)&&(c=!0);if(c)return"."==a.peek()&&a.backUp(1),"number";c=!1;a.match(/^-?0x[0-9a-f]+/i)&&(c=!0);a.match(/^-?[1-9]\d*(e[\+\-]?\d+)?/)&&(c=!0);a.match(/^-?0(?![\dx])/i)&&(c=!0);
if(c)return"number"}if(a.match(v))return b.tokenize=p(a.current(),!1,"string"),b.tokenize(a,b);if(a.match(w)){if("/"!=a.current()||a.match(/^.*\//,!1))return b.tokenize=p(a.current(),!0,"string-2"),b.tokenize(a,b);a.backUp(1)}if(a.match(x)||a.match(y))return"operator";if(a.match(z))return"punctuation";if(a.match(A))return"atom";if(a.match(B)||b.prop&&a.match(q))return"property";if(a.match(C))return"keyword";if(a.match(q))return"variable";a.next();return"error"}function p(a,b,c){return function(d,
f){for(;!d.eol();)if(d.eatWhile(/[^'"\/\\]/),d.eat("\\")){if(d.next(),b&&d.eol())return c}else{if(d.match(a))return f.tokenize=h,c;d.eat(/['"\/]/)}b&&(t.singleLineStringErrors?c="error":f.tokenize=h);return c}}function u(a,b){for(;!a.eol();){a.eatWhile(/[^#]/);if(a.match("###")){b.tokenize=h;break}a.eatWhile("#")}return"comment"}function n(a,b,c){c=c||"coffee";for(var d=0,f=!1,r=null,g=b.scope;g;g=g.prev)if("coffee"===g.type||"}"==g.type){d=g.offset+e.indentUnit;break}"coffee"!==c?(f=null,r=a.column()+
a.current().length):b.scope.align&&(b.scope.align=!1);b.scope={offset:d,type:c,prev:b.scope,align:f,alignOffset:r}}function m(a,b){if(b.scope.prev){if("coffee"===b.scope.type){a=a.indentation();for(var c=!1,d=b.scope;d;d=d.prev)if(a===d.offset){c=!0;break}if(!c)return!0;for(;b.scope.prev&&b.scope.offset!==a;)b.scope=b.scope.prev}else b.scope=b.scope.prev;return!1}}var x=/^(?:->|=>|\+[+=]?|-[\-=]?|\*[\*=]?|\/[\/=]?|[=!]=|<[><]?=?|>>?=?|%=?|&=?|\|=?|\^=?|\~|!|\?|(or|and|\|\||&&|\?)=)/,z=/^(?:[()\[\]{},:`=;]|\.\.?\.?)/,
q=/^[_A-Za-z$][_A-Za-z$0-9]*/,B=/^@[_A-Za-z$][_A-Za-z$0-9]*/,y=k("and or not is isnt in instanceof typeof".split(" ")),l="for while loop if unless else switch try catch finally class".split(" "),C=k(l.concat("break by continue debugger delete do in of new return then this @ throw when until extends".split(" "))),l=k(l),v=/^('{3}|\"{3}|['\"])/,w=/^(\/{3}|\/)/,A=k("Infinity NaN undefined null true false on off yes no".split(" "));return{startState:function(a){return{tokenize:h,scope:{offset:a||0,type:"coffee",
prev:null,align:!1},prop:!1,dedent:0}},token:function(a,b){var c=null===b.scope.align&&b.scope;c&&a.sol()&&(c.align=!1);var d;d=b.tokenize(a,b);var f=a.current();"return"===f&&(b.dedent=!0);(("->"===f||"=>"===f)&&a.eol()||"indent"===d)&&n(a,b);var e="[({".indexOf(f);-1!==e&&n(a,b,"])}".slice(e,e+1));l.exec(f)&&n(a,b);"then"==f&&m(a,b);if("dedent"===d&&m(a,b))d="error";else{e="])}".indexOf(f);if(-1!==e){for(;"coffee"==b.scope.type&&b.scope.prev;)b.scope=b.scope.prev;b.scope.type==f&&(b.scope=b.scope.prev)}b.dedent&&
a.eol()&&("coffee"==b.scope.type&&b.scope.prev&&(b.scope=b.scope.prev),b.dedent=!1)}d&&"comment"!=d&&(c&&(c.align=!0),b.prop="punctuation"==d&&"."==a.current());return d},indent:function(a,b){if(a.tokenize!=h)return 0;a=a.scope;var c=b&&-1<"])}".indexOf(b.charAt(0));if(c)for(;"coffee"==a.type&&a.prev;)a=a.prev;b=c&&a.type===b.charAt(0);return a.align?a.alignOffset-(b?1:0):(b?a.prev:a).offset},lineComment:"#",fold:"indent"}});e.defineMIME("text/x-coffeescript","coffeescript");e.defineMIME("text/coffeescript",
"coffeescript")});
