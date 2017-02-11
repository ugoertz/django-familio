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
        $.get(
                "{% url urldata %}",
                { link: source[0].{% firstof get_href "href" %} },
                function (data) {
                    source.popover({
                        // placement: "auto left",
                        placement: function (context, source) {
                            // var position = $(source).position();
                            // console.log($(source).position());
                            return "auto left";
                        },
                        html: true,
                        show: true,
                        container: 'body',
                        content: data
                    }).popover('show');
                    source.attr('has_popover', true);
                });
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

