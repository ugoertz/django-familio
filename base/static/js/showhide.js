function show_hide_button(button_location, toggled_element, identifier) {
    $(button_location).append('<span class="btn btn-default btn-xs pull-right" id="showhidebtn-' + identifier + '">Verbergen</span>')
    $('#showhidebtn-' + identifier).click(function() {
        $(toggled_element).toggle(500);
        if ($('#showhidebtn-' + identifier).html() == 'Verbergen') {
            $('#showhidebtn-' + identifier).html('Anzeigen')
        } else {
            $('#showhidebtn-' + identifier).html('Verbergen')
        }
    });
}

