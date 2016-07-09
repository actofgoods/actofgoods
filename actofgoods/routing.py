from channels.routing import route
from basics import consumers


channel_routing = [
    route('websocket.receive', consumers.ws_echo),
    route('websocket.connect', consumers.ws_add,
          path=r'^/chat/(?P<room>\w+)$'),
]
