var popover_timer;

$('{{ selector }}').hover(
function() {
    if (popover_timer) {
        clearTimeout(popover_timer);
        popover_timer = null;
    }
    var source = $(this);

    popover_timer = setTimeout(function() {
        // source.off('hover')
        if (source.attr('has_popover')) {
            source.popover('show');
            return
        }
        {{ fct }}(function (data) {
            source.popover({
                placement: "auto left",
                html: true,
                show: true,
                container: 'body',
                content: data
            }).popover('show');
            source.attr('has_popover', true);
        }, {link: source[0].{% firstof get_href "href" %} });
    }, 400);
},
function() {
    $(this).popover('hide');
    if (popover_timer) {
        clearTimeout(popover_timer);
        popover_timer = null;
    }
}
);

$('body').click(function() {
    $('{{ selector }}').each(
            function() {
                $(this).popover('hide');
                if (popover_timer) {
                    clearTimeout(popover_timer);
                    popover_timer = null;
                }
            }
            )
});

