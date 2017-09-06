$('.like_post').click(function(){
    var postid = $(this).attr("data-postid");
    var profileid = $(this).attr("data-profileid");
    var count = $(this).parent().find('.post_likes_count');
    var button = $(this)
    $.get('/like_post/', {post_id: postid, profile_id: profileid}, function(data){
        count.html(data['likes']);
        button.html(data['button']);
    });
});
$('.like_comment').click(function(){
    var commentid = $(this).attr("data-commentid");
    var profileid = $(this).attr("data-profileid");
    var count = $(this).parent().find('.comment_likes_count');
    var button = $(this)
    $.get('/like_comment/', {comment_id: commentid, profile_id: profileid}, function(data){
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