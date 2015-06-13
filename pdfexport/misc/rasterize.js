// adapted from the rasterize.js example coming with PhantomJS
//
// Edit the fillLoginInfo function below (i.e., add credentials for logging into
// the web site) and put this file into the same directory as the phantomjs
// binary (as referenced in the settings file)


var page = require('webpage').create(),
    system = require('system'),
    address, output, size;

page.settings.resourceTimeout = 10000;

address = system.args[1];
output = system.args[2];
// page.viewportSize = { width: 1500, height: 1500 };
if (system.args.length > 3 && system.args[2].substr(-4) === ".pdf") {
    size = system.args[3].split('*');
    page.paperSize = size.length === 2 ? { width: size[0], height: size[1], margin: '0px' }
                                        : { format: system.args[3], orientation: 'portrait', margin: '1cm' };
}

var fillLoginInfo = function(){
    var frm = document.getElementById("login_form");
    $("#id_identification").val("username");
    $("#id_password").val("password");
    frm.submit();
}

page.onLoadFinished = function(){
    if(page.title == "Unsere Familiengeschichte - Anmeldung"){
        page.evaluate(fillLoginInfo);
        return;
    }
    else {
        // currently clipRect is ignored for pdf output (so we have to apply
        // pdfcrop afterwards ...)
        page.clipRect = page.evaluate(function() {
            return document.getElementById("familytree_svg").getBoundingClientRect();
        });
        page.render(output);
        phantom.exit();
    }
}


page.open(address);
