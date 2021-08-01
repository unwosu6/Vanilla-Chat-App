$(function(){
    
    var $publicChats = $('#public-chats');
    var $privateChats = $('#private-chats')
    var $user_id = $('#hidden-user-id').text()
    $.ajax({
        type: 'GET',
        url: '/api/profile/PublicChats/' + $user_id,
        success: function(publicChats) {
            $.each(publicChats, function(i, chat) {
                $publicChats.append('<div class="jumbotron">' +
                '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                '<p class="lead">[' + chat.description + ']</p>' +
                '<hr class="my-4">' +
                '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                '</div>');
            });
        }
    });
    
    $.ajax({
        type: 'GET',
        url: '/api/profile/PrivateChats/' + $user_id,
        success: function(privateChats) {
            $.each(privateChats, function(i, chat) {
                $privateChats.append('<div class="jumbotron">' +
                '<h1 class="display-4">[' + chat.display_name + ']</h1>' +
                '<p class="lead">[' + chat.description + ']</p>' +
                '<hr class="my-4">' +
                '<p>' + chat.num_users + ' members<br> [owner] ' + chat.owner + '<br> [chat code] ' + chat.chatname + '</p>' +
                '<p class="lead"><a class="btn btn-primary btn-lg" href="/' + chat.id + '" role="button">join</a></p>' +
                '</div>');
            });
        }
    });
});
