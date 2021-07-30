$(function(){
    var $userdata = $('#userdata');
    $.ajax({
        type: 'GET',
        url: '/api/AllUsers',
        success: function(userdata) {
            $.each(userdata, function(i, userdatapoint) {
                $userdata.append('<p>' + userdatapoint.password + '</p>');
            });
        }
    });  
});