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
$('.edit_note').click(function(){
    var noteid = $(this).attr("data-noteid");
    var noteclass = $(this).attr("data-class");
    var current_text = $(this).attr("data-text");
    var note_text = $(this).parent();
    $.get('/edit_note_form/', {note_id: noteid, note_class: noteclass}, function(data){
        note_text.html(data);
        note_text.find(".note_text").text(current_text);
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
$("#send_friend_request").click(function(){
    var profileid = $(this).attr("data-profileid");
    var requesterid = $(this).attr("data-requesterid");
    $.get('/send_friend_request/', {requester_id: requesterid, profile_id: profileid}, function(data){
        $('#user_relation_status').html("Friend request pending...<button id=\"cancel_friend_request\" data-profileid=\"{{userprofile.id}}\">Cancel</button>");
    });
});
