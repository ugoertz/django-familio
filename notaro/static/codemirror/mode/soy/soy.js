'use strict';(function(d){"object"==typeof exports&&"object"==typeof module?d(require("../../lib/codemirror"),require("../htmlmixed/htmlmixed")):"function"==typeof define&&define.amd?define(["../../lib/codemirror","../htmlmixed/htmlmixed"],d):d(CodeMirror)})(function(d){var l="template literal msg fallbackmsg let if elseif else switch case default foreach ifempty for call param deltemplate delcall log".split(" ");d.defineMode("soy",function(e){function g(b){return b[b.length-1]}function m(b,a,c){var d=
b.string;if(c=c.exec(d.substr(b.pos)))b.string=d.substr(0,b.pos+c.index);c=b.hideFirstChars(a.indent,function(){return a.localMode.token(b,a.localState)});b.string=d;return c}function h(b,a){return{element:a,next:b}}function n(b,a,c){a:{for(;b;){if(b.element===a){a=!0;break a}b=b.next}a=!1}return a?"variable-2":c?"variable":"variable-2 error"}var k=d.getMode(e,"text/plain"),f={html:d.getMode(e,{name:"text/html",multilineTagIndentFactor:2,multilineTagIndentPastTag:!1}),attributes:k,text:k,uri:k,css:d.getMode(e,
"text/css"),js:d.getMode(e,{name:"text/javascript",statementIndent:2*e.indentUnit})};return{startState:function(){return{kind:[],kindTag:[],soyState:[],templates:null,variables:null,scopes:null,indent:0,localMode:f.html,localState:d.startState(f.html)}},copyState:function(b){return{tag:b.tag,kind:b.kind.concat([]),kindTag:b.kindTag.concat([]),soyState:b.soyState.concat([]),templates:b.templates,variables:b.variables,scopes:b.scopes,indent:b.indent,localMode:b.localMode,localState:d.copyState(b.localMode,
b.localState)}},token:function(b,a){var c;switch(g(a.soyState)){case "comment":return b.match(/^.*?\*\//)?a.soyState.pop():b.skipToEnd(),"comment";case "templ-def":if(c=b.match(/^\.?([\w]+(?!\.[\w]+)*)/))return a.templates=h(a.templates,c[1]),a.scopes=h(a.scopes,a.variables),a.soyState.pop(),"def";b.next();return null;case "templ-ref":if(c=b.match(/^\.?([\w]+)/))return a.soyState.pop(),"."==c[0][0]?n(a.templates,c[1],!0):"variable";b.next();return null;case "param-def":if(c=b.match(/^([\w]+)(?=:)/))return a.variables=
h(a.variables,c[1]),a.soyState.pop(),a.soyState.push("param-type"),"def";b.next();return null;case "param-type":if("}"==b.peek())return a.soyState.pop(),null;if(b.eatWhile(/^[\w]+/))return"variable-3";b.next();return null;case "var-def":if(c=b.match(/^\$([\w]+)/))return a.variables=h(a.variables,c[1]),a.soyState.pop(),"def";b.next();return null;case "tag":if(b.match(/^\/?}/)){if("/template"==a.tag||"/deltemplate"==a.tag)b=a.scopes,a.variables=a.scopes=b&&b.next,a.indent=0;else{if("/for"==a.tag||"/foreach"==
a.tag)c=a.scopes,a.variables=a.scopes=c&&c.next;a.indent-=e.indentUnit*("/}"==b.current()||-1==l.indexOf(a.tag)?2:1)}a.soyState.pop();return"keyword"}if(b.match(/^([\w?]+)(?==)/))return"kind"==b.current()&&(c=b.match(/^="([^"]+)/,!1))&&(b=c[1],a.kind.push(b),a.kindTag.push(a.tag),a.localMode=f[b]||f.html,a.localState=d.startState(a.localMode)),"attribute";if(b.match(/^"/))return a.soyState.push("string"),"string";if(c=b.match(/^\$([\w]+)/))return n(a.variables,c[1]);if(b.match(/(?:as|and|or|not|in)/))return"keyword";
b.next();return null;case "literal":return b.match(/^(?=\{\/literal})/)?(a.indent-=e.indentUnit,a.soyState.pop(),this.token(b,a)):m(b,a,/\{\/literal}/);case "string":return(c=b.match(/^.*?("|\\[\s\S])/))?'"'==c[1]&&a.soyState.pop():b.skipToEnd(),"string"}if(b.match(/^\/\*/))return a.soyState.push("comment"),"comment";if(b.match(b.sol()?/^\s*\/\/.*/:/^\s+\/\/.*/))return"comment";if(b.match(/^\{literal}/))return a.indent+=e.indentUnit,a.soyState.push("literal"),"keyword";if(c=b.match(/^\{([\/@\\]?[\w?]*)/)){"/switch"!=
c[1]&&(a.indent+=(/^(\/|(else|elseif|ifempty|case|default)$)/.test(c[1])&&"switch"!=a.tag?1:2)*e.indentUnit);a.tag=c[1];a.tag=="/"+g(a.kindTag)&&(a.kind.pop(),a.kindTag.pop(),a.localMode=f[g(a.kind)]||f.html,a.localState=d.startState(a.localMode));a.soyState.push("tag");"template"!=a.tag&&"deltemplate"!=a.tag||a.soyState.push("templ-def");"call"!=a.tag&&"delcall"!=a.tag||a.soyState.push("templ-ref");"let"==a.tag&&a.soyState.push("var-def");if("for"==a.tag||"foreach"==a.tag)a.scopes=h(a.scopes,a.variables),
a.soyState.push("var-def");a.tag.match(/^@param\??/)&&a.soyState.push("param-def");return"keyword"}return m(b,a,/\{|\s+\/\/|\/\*/)},indent:function(b,a){var c=b.indent,f=g(b.soyState);if("comment"==f)return d.Pass;if("literal"==f)/^\{\/literal}/.test(a)&&(c-=e.indentUnit);else{if(/^\s*\{\/(template|deltemplate)\b/.test(a))return 0;/^\{(\/|(fallbackmsg|elseif|else|ifempty)\b)/.test(a)&&(c-=e.indentUnit);"switch"!=b.tag&&/^\{(case|default)\b/.test(a)&&(c-=e.indentUnit);/^\{\/switch\b/.test(a)&&(c-=
e.indentUnit)}c&&b.localMode.indent&&(c+=b.localMode.indent(b.localState,a));return c},innerMode:function(b){return b.soyState.length&&"literal"!=g(b.soyState)?null:{state:b.localState,mode:b.localMode}},electricInput:/^\s*\{(\/|\/template|\/deltemplate|\/switch|fallbackmsg|elseif|else|case|default|ifempty|\/literal\})$/,lineComment:"//",blockCommentStart:"/*",blockCommentEnd:"*/",blockCommentContinue:" * ",fold:"indent"}},"htmlmixed");d.registerHelper("hintWords","soy",l.concat("delpackage namespace alias print css debugger".split(" ")));
d.defineMIME("text/x-soy","soy")});
