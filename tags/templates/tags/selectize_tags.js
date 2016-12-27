$('#id_tags{{ object.id }}').selectize({
    valueField: 'id',
    searchField: ['label'],
    closeAfterSelect: true,
    maxItems: 25,
    preload: true,
    searchField: ['id', 'label'],
    render: {
        option:
            function (item, escape) {
                if (item.id.slice(0,4) == "new-") {
                    return "<div class=\"cabin\">" + escape(item.label) + " als neues Schlagwort hinzufügen</div>";
                } else {
                    return "<div class=\"cabin\">" + escape(item.label) + "</div>";
                }
            },
        item:
            function (item, escape) {
                return '<div style="background-color: ' + item.bg_color + ';" class="cabin">' + escape(item.tag) + "</div>";
            }
    },
    create: false,
    load: function(query, callback) {
        $.get("{% url 'get-tags' %}", {query: query}, callback);
    }
});

{% for tag in object.tags.all %}
if ("{{ tag.name }}".slice(0,4) == "tag-") {
    tag_label = "{{ tag.name }}".slice(4);
    bg_color = "#eeeeee";
} else {
    tag_label = "{{ tag.name }}".split(' ').slice(0, -1).join(' ');
    handle = "{{ tag.name }}".split(' ').slice(-1)[0];
    bg_color = 'red';
    if (handle.lastIndexOf('genealogio.person', 0) == 0) bg_color = 'lightgreen';
    else if (handle.lastIndexOf('genealogio.family', 0) == 0) bg_color = 'lightblue';
    else if (handle.lastIndexOf('genealogio.event', 0) == 0) bg_color = 'yellow';
    else if (handle.lastIndexOf('maps.place', 0) == 0) bg_color = 'orange';
}
$('#id_tags{{ object.id }}')[0].selectize.addOption(
        [{'id': '{{ tag.name }}', 'tag': tag_label, 'label': tag_label, 'bg_color': bg_color }]);
$('#id_tags{{ object.id }}')[0].selectize.addItem('{{ tag.name }}');
{% endfor %}
