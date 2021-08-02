$(function(){
    
    var $publicChats = $('#sidebarPublicChats');
    var $privateChats = $('#sidebarPrivateChats');
    var $user_id = $('#hidden-user-id').text();
    var $chat_id = $('#hidden-chat-id').text()
    $.ajax({
        type: 'GET',
        url: '/api/profile/PublicChats/' + $user_id,
        success: function(publicChats) {
            $.each(publicChats, function(i, chat) {
                var buttonType = ""
                if (chat.id == $chat_id) {
                    buttonType = "green-nav"
                }
                    $publicChats.append('<li class="nav-item">' +
                    '<a href="/' + chat.id + ' "class="nav-link sidebar-link ' + buttonType + '" aria-current="page">' +
                    '[' + chat.display_name + ']' +
                    '</a></li>');    
            });
        }
    });
    
    $.ajax({
        type: 'GET',
        url: '/api/profile/PrivateChats/' + $user_id,
        success: function(privateChats) {
            $.each(privateChats, function(i, chat) {
                var buttonType = ""
                if (chat.id == $chat_id) {
                    buttonType = "green-nav"
                }
                    $privateChats.append('<ul class="nav nav-pills flex-column mb-auto">' +
                    '<li class="nav-item">' +
                    '<a href="/' + chat.id + ' "class="nav-link sidebar-link ' + buttonType + '" aria-current="page">' +
                    '[' + chat.display_name + ']' +
                    '</a></li></ul>');    
            });
        }
    });
    
});
