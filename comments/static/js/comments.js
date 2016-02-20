$(document).ready(function(){
    $("#commenters").on("click", ".reply", function(event){
        event.preventDefault();
        var form = $("#postcomment").clone(true);
        var parnt = $(this).parent().parent().parent().parent().attr('id');
        form.find('.parent').val(parnt);
        form.prop('id', 'postcomment' + parnt);
        $(this).parent().parent().append(form);
    });
});
