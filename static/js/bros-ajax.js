$('#like_post').click(function(){
    var postid;
    postid = $(this).attr("data-postid");
    var profileid;
    profileid = $(this).attr("data-profileid");
    $.get('/like_post/', {post_id: postid, profile_id: profileid}, function(data){
        $('#post_likes_count').html(data['likes']);
        $('#like_post').html(data['button']);
    });
});
$('#like_comment').click(function(){
    var commentid;
    commentid = $(this).attr("data-commentid");
    var profileid;
    profileid = $(this).attr("data-profileid");
    $.get('/like_comment/', {comment_id: commentid, profile_id: profileid}, function(data){
        $('#comment_likes_count').html(data);
    });
});
