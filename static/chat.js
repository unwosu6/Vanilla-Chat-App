var current;
$(function(){
    current = $('#hidden-chat-num').text()-1
});
$(setInterval(function(){
    var $allMessages = $('#all-msgs');
    var $user_id = $('#hidden-user-id').text();
    var $chat_id = $('#hidden-chat-id').text();
    $.ajax({
        type: 'GET',
        url: '/api/chat/' + $chat_id + '/messages',
        success: function(allMessages) {
            var total_msgs = Object.keys(allMessages).length;
//             var current = Object.keys($allMessages).length;
//             var current = $('#hidden-chat-num').text() + 1;
            console.log(current)
            console.log(total_msgs)
            if(total_msgs != current){
                $('#all-msgs').empty()
                current =  current + 1;
            $.each(allMessages, function(i, msg) {
                if (msg.user_sent_id != $user_id) {
                    if (msg.content.includes("https://www.youtube.com/embed/")){
                        $allMessages.append(
                        '<div class="incoming_msg">' +
                        '<div class="incoming_msg_img"> <a href="/profiles/' + msg.user_sent_id + '"><img src="' + msg.user_sent_pfp + '" alt="user-profie-pic" class="rounded-circle"></a> </div>' +
                        '<div class="received_msg">' +
                        '<div class="received_withd_msg">' +
                        '<iframe width="560" height="315" src=' + msg.content + ' frameborder="0" allowfullscreen></iframe>' +
                        '<span class="time_date">' + msg.user_sent_display_name + '    |    ' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div></div>'
                    );
                    } else if (msg.content.includes("https://giphy.com/embed/")){
                        $allMessages.append(
                        '<div class="incoming_msg">' +
                        '<div class="incoming_msg_img"> <a href="/profiles/' + msg.user_sent_id + '"><img src="' + msg.user_sent_pfp + '" alt="user-profie-pic" class="rounded-circle"></a> </div>' +
                        '<div class="received_msg">' +
                        '<div class="received_withd_msg">' +
                        '<iframe src="' + msg.content + '" width="480" height="270" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>' +
                        '<span class="time_date">' + msg.user_sent_display_name + '    |    ' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div></div>'
                    );
                    } else {
                        $allMessages.append(
                        '<div class="incoming_msg">' +
                        '<div class="incoming_msg_img"> <a href="/profiles/' + msg.user_sent_id + '"><img src="' + msg.user_sent_pfp + '" alt="user-profie-pic" class="rounded-circle"></a> </div>' +
                        '<div class="received_msg">' +
                        '<div class="received_withd_msg">' +
                        '<p>' + msg.content + '</p>' +
                        '<span class="time_date">' + msg.user_sent_display_name + '    |    ' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div></div>'
                    );
                    }
                } else {
                    if (msg.content.includes("https://www.youtube.com/embed/")){
                        $allMessages.append(
                        '<div class="outgoing_msg">' +
                        '<div class="sent_msg">' +
                        '<iframe width="560" height="315" src=' + msg.content + ' frameborder="0" allowfullscreen></iframe>' +
                        '<span class="time_date">' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div>'
                    );
                    } else if (msg.content.includes("https://giphy.com/embed/")){
                        $allMessages.append(
                        '<div class="outgoing_msg">' +
                        '<div class="sent_msg">' +
                        '<iframe src="' + msg.content + '" width="480" height="270" frameBorder="0" class="giphy-embed" allowFullScreen></iframe>' +
                        '<span class="time_date">' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div>'
                    );
                    } else{
                        $allMessages.append(
                        '<div class="outgoing_msg">' +
                        '<div class="sent_msg">' +
                        '<p>' + msg.content + '</p>' +
                        '<span class="time_date">' + msg.time + '    |    ' + msg.date + '</span></div>' +
                        '</div>'
                    );
                    }
                }
             });
            }
        }
    });
}, 1000)
);
// $(document).ajaxStop(function(){
//         window.location.reload();
//     }
// });