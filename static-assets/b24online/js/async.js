/**
 * Created by user on 19.02.14.
 */
$(document).ready(function() {
    socket_connect();

    function socket_connect() {
        return;
        socket = new SockJS('/echo');
        socket.onmessage = function(msg){
            var data = msg['data'];
            var data = JSON.parse(data);
            var type = data.type;
            data = data.data;

            if (type == 'notification') {
                el = $(".imgnews.icon-nt1");
                num = el.siblings(".num").text();
                el.siblings(".num").text(parseInt(num) + 1);
            } else if (type == 'private_message') {
                el = $("#mailcounter");
                num = el.text();
                el.text(parseInt(num) + 1);
                if(window.location.href.indexOf("messages") > -1){
                    $(document).trigger('new_message', [data.fromUser]);
                }
            }
        }

        socket.onclose = function(e){
            setTimeout(socket_connect, 5000);
        };
    }
});
