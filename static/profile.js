$(function(){
    
    var $publicChats = $('#public-chats');
    var $privateChats = $('#private-chats');
    var $sharedPrivateChats = $('#shared-private-chats');
    var $user_id = $('#hidden-user-id').text();
    var $other_user_id = $('#hidden-other-user-id').text();
    var $current_user = $('#hidden-curr-user-id').text();
    $.ajax({
        type: 'GET',
        url: '/api/profile/PublicChats/' + $user_id,
        success: function(publicChats) {
            $.each(publicChats, function(i, chat) {
                if (chat.owner_id == $current_user) {
                    $publicChats.append('<div class="jumbotron">' +
                    '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                    '<p class="lead">[' + chat.description + ']</p>' +
                    '<hr class="my-4">' +
                    '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/edit_chat/' + chat.id + '" role="button">edit</a></p>' +
                    '</div>');
                } else {
                    $publicChats.append('<div class="jumbotron">' +
                    '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                    '<p class="lead">[' + chat.description + ']</p>' +
                    '<hr class="my-4">' +
                    '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                    '</div>');    
                }
            });
        }
    });
    
    $.ajax({
        type: 'GET',
        url: '/api/profile/PrivateChats/' + $user_id,
        success: function(privateChats) {
            $.each(privateChats, function(i, chat) {
                if (chat.owner_id == $current_user) {
                    $publicChats.append('<div class="jumbotron">' +
                    '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                    '<p class="lead">[' + chat.description + ']</p>' +
                    '<hr class="my-4">' +
                    '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/edit_chat/' + chat.id + '" role="button">edit</a></p>' +
                    '</div>');
                } else {
                    $privateChats.append('<div class="jumbotron">' +
                    '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                    '<p class="lead">[' + chat.description + ']</p>' +
                    '<hr class="my-4">' +
                    '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                    '</div>');
                }
            });
        }
    });
    
    $.ajax({
        type: 'GET',
        url: '/api/profile/PrivateChats/' + $user_id + "/" + $other_user_id,
        success: function(sharedPrivateChats) {
            $.each(sharedPrivateChats, function(i, chat) {
                if (chat.owner_id == $current_user) {
                    $publicChats.append('<div class="jumbotron">' +
                    '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                    '<p class="lead">[' + chat.description + ']</p>' +
                    '<hr class="my-4">' +
                    '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/edit_chat/' + chat.id + '" role="button">edit</a></p>' +
                    '</div>');
                } else {
                    $sharedPrivateChats.append('<div class="jumbotron">' +
                    '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                    '<p class="lead">[' + chat.description + ']</p>' +
                    '<hr class="my-4">' +
                    '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                    '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                    '</div>');
                }
            });
        }
    });
});
