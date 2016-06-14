from channels.routing import route


channel_routing = [
    route('websocket.receive', 'basics.consumers.ws_echo'),
    route('websocket.connect', 'basics.consumers.ws_add',
          path=r'^/chat/(?P<room>\w+)$'),
]
