$(function(){
    var $allMessages = $('#all-msgs')
    var $user_id = $('#hidden-user-id').text()
    var $chat_id = $('#hidden-chat-id').text()
    $.ajax({
        type: 'GET',
        url: '/api/chat/' + $chat_id + '/messages',
        success: function(allMessages) {
            $.each(allMessages, function(i, msg) {
                if (msg.user_sent_id != $user_id) {
                    if (msg.content.includes("https://www.youtube.com/embed/")){
                        
                    } else{
                        
                    }
                    $allMessages.append(
                        '<div class="incoming_msg">' +
                        '<div class="incoming_msg_img"> <img src="' + msg.user_sent_pfp + '" alt="user-profie-pic"> </div>' +
                        '<div class="received_msg">' +
                        '<div class="received_withd_msg">' +
                        '<p>' + msg.content + '</p>' +
                        '<span class="time_date">' + msg.user_sent_display_name + '    |    ' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div></div>'
                    );
                } else {
                    $allMessages.append(
                        '<div class="outgoing_msg">' +
                        '<div class="sent_msg">' +
                        '<p>' + msg.content + '</p>' +
                        '<span class="time_date">' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div>'
                    );
                }
             });
        }
    });
});
