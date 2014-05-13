/**
 * Created by user on 19.02.14.
 */
$(document).ready(function() {
       socket_connect();

        function socket_connect() {
            socket = new SockJS('http://' + window.location.host + ':9999/orders');  // ваш порт для асинхронного сервиса
            // при соединении вызываем событие login, которое будет выполнено на серверной стороне

            socket.onmessage = function(msg){
                var data = msg['data']
                var data = JSON.parse(data)
                var type = data.type
                data = data.data

                if (type == 'notification')
                {
                    el = $(".imgnews.i-note")
                    num = el.siblings(".num").text()
                    el.siblings(".num").text(parseInt(num)+1)
                }
                else if (type == 'private_massage')
                {


                    el = $(".imgnews.i-mail")
                    num = el.siblings(".num").text()

                    el.siblings(".num").text(parseInt(num)+1)
                    $(document).trigger('new_message', [data.fromUser])

                }
            }

            socket.onclose = function(e){
                setTimeout(socket_connect, 5000);
            };
        }
});