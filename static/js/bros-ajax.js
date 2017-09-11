$('.like').click(function(){
    var objectid = $(this).attr("data-objectid");
    var profileid = $(this).attr("data-profileid");
    var objectclass = $(this).attr("data-class");
    var count = $(this).parent().find('.likes_count');
    var button = $(this)
    $.get('/like/', {object_id: objectid, profile_id: profileid, object_class: objectclass}, function(data){
        count.html(data['likes']);
        button.html(data['button']);
    });
});
$('.edit_post').click(function(){
    var postid = $(this).attr("data-postid");
    var current_text = $(this).attr("data-text");
    var post_text = $(this).parent();
    $.get('/edit_post/', {post_id: postid}, function(data){
        post_text.html(data);
        post_text.find(".post_text").text(current_text);
    });
});
$('.edit_comment').click(function(){
    var commentid = $(this).attr("data-commentid");
    var current_text = $(this).attr("data-text")
    var comment_text = $(this).parent();
    $.get('/edit_comment/', {comment_id: commentid}, function(data){
        comment_text.html(data);
        comment_text.find(".comment_text").text(current_text);
    });
});
$(".search-form .search-input").keyup(function(){
    var query = $(this).val();

    $.get('/search/', {suggestion: query}, function(data){
        $('.search-form #suggestions').html(data);
    });
});
$(".search-input").on('input', function () {
    var val = this.value;
    var chosen;
    if($('#suggestions option').filter(function(){
        chosen = $(this)
        return this.value === val;
    }).length) {
        window.location.href = chosen.data("url");
    }
});

