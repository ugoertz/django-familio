'use strict';(function(p){"object"==typeof exports&&"object"==typeof module?p(require("../../lib/codemirror")):"function"==typeof define&&define.amd?define(["../../lib/codemirror"],p):p(CodeMirror)})(function(p){function ha(p,q,n){return/^(?:operator|sof|keyword c|case|new|export|default|[\[{}\(,;:]|=>)$/.test(q.lastType)||"quasi"==q.lastType&&/\{\s*$/.test(p.string.slice(0,p.pos-(n||0)))}p.defineMode("javascript",function(wa,q){function n(a,c,b){F=a;N=b;return c}function y(a,c){var b=a.next();if('"'==
b||"'"==b)return c.tokenize=xa(b),c.tokenize(a,c);if("."==b&&a.match(/^\d+(?:[eE][+\-]?\d+)?/))return n("number","number");if("."==b&&a.match(".."))return n("spread","meta");if(/[\[\]{}\(\),;\:\.]/.test(b))return n(b);if("="==b&&a.eat(">"))return n("=>","operator");if("0"==b&&a.eat(/x/i))return a.eatWhile(/[\da-f]/i),n("number","number");if("0"==b&&a.eat(/o/i))return a.eatWhile(/[0-7]/i),n("number","number");if("0"==b&&a.eat(/b/i))return a.eatWhile(/[01]/i),n("number","number");if(/\d/.test(b))return a.match(/^\d*(?:\.\d*)?(?:[eE][+\-]?\d+)?/),
n("number","number");if("/"==b){if(a.eat("*"))return c.tokenize=O,O(a,c);if(a.eat("/"))return a.skipToEnd(),n("comment","comment");if(ha(a,c,1)){a:for(var e=c=!1;null!=(b=a.next());){if(!c){if("/"==b&&!e)break a;"["==b?e=!0:e&&"]"==b&&(e=!1)}c=!c&&"\\"==b}a.match(/^\b(([gimyu])(?![gimyu]*\2))+\b/);return n("regexp","string-2")}a.eatWhile(P);return n("operator","operator",a.current())}if("`"==b)return c.tokenize=X,X(a,c);if("#"==b)return a.skipToEnd(),n("error","error");if(P.test(b))return">"==b&&
c.lexical&&">"==c.lexical.type||a.eatWhile(P),n("operator","operator",a.current());if(Y.test(b))return a.eatWhile(Y),a=a.current(),(b=ia.propertyIsEnumerable(a)&&ia[a])&&"."!=c.lastType?n(b.type,b.style,a):n("variable","variable",a)}function xa(a){return function(c,b){var e=!1,k;if(Q&&"@"==c.peek()&&c.match(ya))return b.tokenize=y,n("jsonld-keyword","meta");for(;null!=(k=c.next())&&(k!=a||e);)e=!e&&"\\"==k;e||(b.tokenize=y);return n("string","string")}}function O(a,c){for(var b=!1,e;e=a.next();){if("/"==
e&&b){c.tokenize=y;break}b="*"==e}return n("comment","comment")}function X(a,c){for(var b=!1,e;null!=(e=a.next());){if(!b&&("`"==e||"$"==e&&a.eat("{"))){c.tokenize=y;break}b=!b&&"\\"==e}return n("quasi","string-2",a.current())}function Z(a,c){c.fatArrowAt&&(c.fatArrowAt=null);var b=a.string.indexOf("=>",a.start);if(!(0>b)){if(z){var e=/:\s*(?:\w+(?:<[^>]*>|\[\])?|\{[^}]*\})\s*$/.exec(a.string.slice(a.start,b));e&&(b=e.index)}for(var e=0,d=!1,b=b-1;0<=b;--b){var A=a.string.charAt(b),f="([{}])".indexOf(A);
if(0<=f&&3>f){if(!e){++b;break}if(0==--e){"("==A&&(d=!0);break}}else if(3<=f&&6>f)++e;else if(Y.test(A))d=!0;else{if(/["'\/]/.test(A))return;if(d&&!e){++b;break}}}d&&!e&&(c.fatArrowAt=b)}}function ja(a,b,d,e,f,A){this.indented=a;this.column=b;this.type=d;this.prev=f;this.info=A;null!=e&&(this.align=e)}function f(){for(var a=arguments.length-1;0<=a;a--)d.cc.push(arguments[a])}function b(){f.apply(null,arguments);return!0}function G(a){function b(b){for(;b;b=b.next)if(b.name==a)return!0;return!1}var k=
d.state;d.marked="def";k.context?b(k.localVars)||(k.localVars={name:a,next:k.localVars}):!b(k.globalVars)&&q.globalVars&&(k.globalVars={name:a,next:k.globalVars})}function H(){d.state.context={prev:d.state.context,vars:d.state.localVars};d.state.localVars=za}function I(){d.state.localVars=d.state.context.vars;d.state.context=d.state.context.prev}function l(a,b){var c=function(){var c=d.state,k=c.indented;if("stat"==c.lexical.type)k=c.lexical.indented;else for(var f=c.lexical;f&&")"==f.type&&f.align;f=
f.prev)k=f.indented;c.lexical=new ja(k,d.stream.column(),a,null,c.lexical,b)};c.lex=!0;return c}function g(){var a=d.state;a.lexical.prev&&(")"==a.lexical.type&&(a.indented=a.lexical.indented),a.lexical=a.lexical.prev)}function h(a){function c(d){return d==a?b():";"==a?f():b(c)}return c}function r(a,c){return"var"==a?b(l("vardef",c.length),aa,h(";"),g):"keyword a"==a?b(l("form"),ba,r,g):"keyword b"==a?b(l("form"),r,g):"{"==a?b(l("}"),R,g):";"==a?b():"if"==a?("else"==d.state.lexical.info&&d.state.cc[d.state.cc.length-
1]==g&&d.state.cc.pop()(),b(l("form"),ba,r,g,ka)):"function"==a?b(w):"for"==a?b(l("form"),Aa,r,g):"variable"==a?b(l("stat"),Ba):"switch"==a?b(l("form"),ba,l("}","switch"),h("{"),R,g,g):"case"==a?b(m,h(":")):"default"==a?b(h(":")):"catch"==a?b(l("form"),H,h("("),ca,h(")"),r,g,I):"class"==a?b(l("form"),la,g):"export"==a?b(l("stat"),Ca,g):"import"==a?b(l("stat"),Da,g):"module"==a?b(l("form"),u,l("}"),h("{"),R,g,g):"type"==a?b(v,h("operator"),v,h(";")):"async"==a?b(r):f(l("stat"),m,h(";"),g)}function m(a){return ma(a,
!1)}function t(a){return ma(a,!0)}function ba(a){return"("!=a?f():b(l(")"),m,h(")"),g)}function ma(a,c){if(d.state.fatArrowAt==d.stream.start){var k=c?na:oa;if("("==a)return b(H,l(")"),x(u,")"),g,h("=>"),k,I);if("variable"==a)return f(H,u,h("=>"),k,I)}k=c?J:B;return Ea.hasOwnProperty(a)?b(k):"function"==a?b(w,k):"class"==a?b(l("form"),Fa,g):"keyword c"==a||"async"==a?b(c?Ga:da):"("==a?b(l(")"),da,h(")"),g,k):"operator"==a||"spread"==a?b(c?t:m):"["==a?b(l("]"),Ha,g,k):"{"==a?K(ea,"}",null,k):"quasi"==
a?f(S,k):"new"==a?b(Ia(c)):b()}function da(a){return a.match(/[;\}\)\],]/)?f():f(m)}function Ga(a){return a.match(/[;\}\)\],]/)?f():f(t)}function B(a,c){return","==a?b(m):J(a,c,!1)}function J(a,c,d){var e=0==d?B:J,k=0==d?m:t;if("=>"==a)return b(H,d?na:oa,I);if("operator"==a)return/\+\+|--/.test(c)?b(e):"?"==c?b(m,h(":"),k):b(k);if("quasi"==a)return f(S,e);if(";"!=a){if("("==a)return K(t,")","call",e);if("."==a)return b(Ja,e);if("["==a)return b(l("]"),da,h("]"),g,e)}}function S(a,c){return"quasi"!=
a?f():"${"!=c.slice(c.length-2)?b(S):b(m,Ka)}function Ka(a){if("}"==a)return d.marked="string-2",d.state.tokenize=X,b(S)}function oa(a){Z(d.stream,d.state);return f("{"==a?r:m)}function na(a){Z(d.stream,d.state);return f("{"==a?r:t)}function Ia(a){return function(c){return"."==c?b(a?La:Ma):f(a?t:m)}}function Ma(a,c){if("target"==c)return d.marked="keyword",b(B)}function La(a,c){if("target"==c)return d.marked="keyword",b(J)}function Ba(a){return":"==a?b(g,r):f(B,h(";"),g)}function Ja(a){if("variable"==
a)return d.marked="property",b()}function ea(a,c){if("async"==a)return d.marked="property",b(ea);if("variable"==a||"keyword"==d.style)return d.marked="property","get"==c||"set"==c?b(Na):b(C);if("number"==a||"string"==a)return d.marked=Q?"property":d.style+" property",b(C);if("jsonld-keyword"==a)return b(C);if("modifier"==a)return b(ea);if("["==a)return b(m,h("]"),C);if("spread"==a)return b(m);if(":"==a)return f(C)}function Na(a){if("variable"!=a)return f(C);d.marked="property";return b(w)}function C(a){if(":"==
a)return b(t);if("("==a)return f(w)}function x(a,c){function k(e,g){return","==e?(e=d.state.lexical,"call"==e.info&&(e.pos=(e.pos||0)+1),b(function(b,e){return b==c||e==c?f():f(a)},k)):e==c||g==c?b():b(h(c))}return function(e,d){return e==c||d==c?b():f(a,k)}}function K(a,c,k){for(var e=3;e<arguments.length;e++)d.cc.push(arguments[e]);return b(l(c,k),x(a,c),g)}function R(a){return"}"==a?b():f(r,R)}function T(a,c){if(z){if(":"==a)return b(v);if("?"==c)return b(T)}}function v(a){if("variable"==a)return d.marked=
"variable-3",b(U);if("string"==a||"number"==a||"atom"==a)return b(U);if("{"==a)return b(x(pa,"}"));if("("==a)return b(x(qa,")"),Oa)}function Oa(a){if("=>"==a)return b(v)}function pa(a){if("variable"==a||"keyword"==d.style)return d.marked="property",b(pa);if(":"==a)return b(v)}function qa(a){if("variable"==a)return b(qa);if(":"==a)return b(v)}function U(a,c){if("<"==c)return b(l(">"),x(v,">"),g,U);if("|"==c||"."==a)return b(v);if("["==a)return b(h("]"),U)}function aa(){return f(u,T,L,Pa)}function u(a,
c){if("modifier"==a)return b(u);if("variable"==a)return G(c),b();if("spread"==a)return b(u);if("["==a)return K(u,"]");if("{"==a)return K(Qa,"}")}function Qa(a,c){if("variable"==a&&!d.stream.match(/^\s*:/,!1))return G(c),b(L);"variable"==a&&(d.marked="property");return"spread"==a?b(u):"}"==a?f():b(h(":"),u,L)}function L(a,c){if("="==c)return b(t)}function Pa(a){if(","==a)return b(aa)}function ka(a,c){if("keyword b"==a&&"else"==c)return b(l("form","else"),r,g)}function Aa(a){if("("==a)return b(l(")"),
Ra,h(")"),g)}function Ra(a){return"var"==a?b(aa,h(";"),V):";"==a?b(V):"variable"==a?b(Sa):f(m,h(";"),V)}function Sa(a,c){return"in"==c||"of"==c?(d.marked="keyword",b(m)):b(B,V)}function V(a,c){return";"==a?b(ra):"in"==c||"of"==c?(d.marked="keyword",b(m)):f(m,h(";"),ra)}function ra(a){")"!=a&&b(m)}function w(a,c){if("*"==c)return d.marked="keyword",b(w);if("variable"==a)return G(c),b(w);if("("==a)return b(H,l(")"),x(ca,")"),g,T,r,I)}function ca(a){return"spread"==a?b(ca):f(u,T,L)}function Fa(a,b){return"variable"==
a?la(a,b):fa(a,b)}function la(a,c){if("variable"==a)return G(c),b(fa)}function fa(a,c){if("extends"==c||"implements"==c)return b(z?v:m,fa);if("{"==a)return b(l("}"),M,g)}function M(a,c){if("variable"==a||"keyword"==d.style){if(("static"==c||"get"==c||"set"==c||z&&("public"==c||"private"==c||"protected"==c||"readonly"==c||"abstract"==c))&&d.stream.match(/^\s+[\w$\xa1-\uffff]/,!1))return d.marked="keyword",b(M);d.marked="property";return b(z?sa:w,M)}if("*"==c)return d.marked="keyword",b(M);if(";"==
a)return b(M);if("}"==a)return b()}function sa(a,c){return"?"==c?b(sa):":"==a?b(v,L):f(w)}function Ca(a,c){return"*"==c?(d.marked="keyword",b(ga,h(";"))):"default"==c?(d.marked="keyword",b(m,h(";"))):"{"==a?b(x(ta,"}"),ga,h(";")):f(r)}function ta(a,c){if("as"==c)return d.marked="keyword",b(h("variable"));if("variable"==a)return f(t,ta)}function Da(a){return"string"==a?b():f(W,ua,ga)}function W(a,c){if("{"==a)return K(W,"}");"variable"==a&&G(c);"*"==c&&(d.marked="keyword");return b(Ta)}function ua(a){if(","==
a)return b(W,ua)}function Ta(a,c){if("as"==c)return d.marked="keyword",b(W)}function ga(a,c){if("from"==c)return d.marked="keyword",b(m)}function Ha(a){return"]"==a?b():f(x(t,"]"))}var D=wa.indentUnit,va=q.statementIndent,Q=q.jsonld,E=q.json||Q,z=q.typescript,Y=q.wordCharacters||/[\w$\xa1-\uffff]/,ia=function(){function a(a){return{type:a,style:"keyword"}}var b=a("keyword a"),d=a("keyword b"),e=a("keyword c"),f=a("operator"),g={type:"atom",style:"atom"},b={"if":a("if"),"while":b,"with":b,"else":d,
"do":d,"try":d,"finally":d,"return":e,"break":e,"continue":e,"new":a("new"),"delete":e,"throw":e,"debugger":e,"var":a("var"),"const":a("var"),let:a("var"),"function":a("function"),"catch":a("catch"),"for":a("for"),"switch":a("switch"),"case":a("case"),"default":a("default"),"in":f,"typeof":f,"instanceof":f,"true":g,"false":g,"null":g,undefined:g,NaN:g,Infinity:g,"this":a("this"),"class":a("class"),"super":a("atom"),yield:e,"export":a("export"),"import":a("import"),"extends":e,await:e,async:a("async")};
if(z){var d={type:"variable",style:"variable-3"},e={"interface":a("class"),"implements":e,namespace:e,module:a("module"),"enum":a("module"),type:a("type"),"public":a("modifier"),"private":a("modifier"),"protected":a("modifier"),"abstract":a("modifier"),as:f,string:d,number:d,"boolean":d,any:d},h;for(h in e)b[h]=e[h]}return b}(),P=/[+\-*&%=<>!?|~^]/,ya=/^@(context|id|value|language|type|container|list|set|reverse|index|base|vocab|graph)"/,F,N,Ea={atom:!0,number:!0,variable:!0,string:!0,regexp:!0,"this":!0,
"jsonld-keyword":!0},d={state:null,column:null,marked:null,cc:null},za={name:"this",next:{name:"arguments"}};g.lex=!0;return{startState:function(a){a={tokenize:y,lastType:"sof",cc:[],lexical:new ja((a||0)-D,0,"block",!1),localVars:q.localVars,context:q.localVars&&{vars:q.localVars},indented:a||0};q.globalVars&&"object"==typeof q.globalVars&&(a.globalVars=q.globalVars);return a},token:function(a,b){a.sol()&&(b.lexical.hasOwnProperty("align")||(b.lexical.align=!1),b.indented=a.indentation(),Z(a,b));
if(b.tokenize!=O&&a.eatSpace())return null;var c=b.tokenize(a,b);if("comment"==F)return c;b.lastType="operator"!=F||"++"!=N&&"--"!=N?F:"incdec";a:{var e=F,f=N,g=b.cc;d.state=b;d.stream=a;d.marked=null;d.cc=g;d.style=c;b.lexical.hasOwnProperty("align")||(b.lexical.align=!0);for(;;)if((g.length?g.pop():E?m:r)(e,f)){for(;g.length&&g[g.length-1].lex;)g.pop()();if(d.marked){c=d.marked;break a}if(a="variable"==e)b:{for(a=b.localVars;a;a=a.next)if(a.name==f){a=!0;break b}for(b=b.context;b;b=b.prev)for(a=
b.vars;a;a=a.next)if(a.name==f){a=!0;break b}a=void 0}if(a){c="variable-2";break a}break a}}return c},indent:function(a,b){if(a.tokenize==O)return p.Pass;if(a.tokenize!=y)return 0;var c=b&&b.charAt(0),e=a.lexical,d;if(!/^\s*else\b/.test(b))for(var f=a.cc.length-1;0<=f;--f){var h=a.cc[f];if(h==g)e=e.prev;else if(h!=ka)break}for(;!("stat"!=e.type&&"form"!=e.type||"}"!=c&&(!(d=a.cc[a.cc.length-1])||d!=B&&d!=J||/^[,\.=+\-*:?[\(]/.test(b)));)e=e.prev;va&&")"==e.type&&"stat"==e.prev.type&&(e=e.prev);d=
e.type;f=c==d;return"vardef"==d?e.indented+("operator"==a.lastType||","==a.lastType?e.info+1:0):"form"==d&&"{"==c?e.indented:"form"==d?e.indented+D:"stat"==d?(c=e.indented,a="operator"==a.lastType||","==a.lastType||P.test(b.charAt(0))||/[,.]/.test(b.charAt(0)),c+(a?va||D:0)):"switch"!=e.info||f||0==q.doubleIndentSwitch?e.align?e.column+(f?0:1):e.indented+(f?0:D):e.indented+(/^(?:case|default)\b/.test(b)?D:2*D)},electricInput:/^\s*(?:case .*?:|default:|\{|\})$/,blockCommentStart:E?null:"/*",blockCommentEnd:E?
null:"*/",lineComment:E?null:"//",fold:"brace",closeBrackets:"()[]{}''\"\"``",helperType:E?"json":"javascript",jsonldMode:Q,jsonMode:E,expressionAllowed:ha,skipExpression:function(a){var b=a.cc[a.cc.length-1];b!=m&&b!=t||a.cc.pop()}}});p.registerHelper("wordChars","javascript",/[\w$]/);p.defineMIME("text/javascript","javascript");p.defineMIME("text/ecmascript","javascript");p.defineMIME("application/javascript","javascript");p.defineMIME("application/x-javascript","javascript");p.defineMIME("application/ecmascript",
"javascript");p.defineMIME("application/json",{name:"javascript",json:!0});p.defineMIME("application/x-json",{name:"javascript",json:!0});p.defineMIME("application/ld+json",{name:"javascript",jsonld:!0});p.defineMIME("text/typescript",{name:"javascript",typescript:!0});p.defineMIME("application/typescript",{name:"javascript",typescript:!0})});
