$(document).ready(function(){
    $("#commenters").on("click", ".reply", function(event){
        event.preventDefault();
        var form = $("#postcomment").clone(true);
        form.find('.parent').val($(this).parent().parent().parent().parent().attr('id'));
        $(this).parent().parent().append(form);
    });
});
