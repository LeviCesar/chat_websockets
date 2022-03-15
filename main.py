from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List

import uvicorn

api = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <style>
            html {
                height: 100%;k
                weight: 100%;
            }
            body {
                margin: 0;
                height: 100%;
                weight: 100%;
            }
            
            h1 {
                text-align: center;
            }
            
            #messagesContent {
                height: 80%;
                weight: 80%;
                align-content: center;
            }
            
            #messageForm {
                display: flex;
                justify-content: center;
            }
        </style>
        <h1>Dev Chat</h1>
        <div id="messagesContent">
            <ul id="messages"></ul>
        </div>
        <form action="" onsubmit="sendMessage(event)" id="messageForm">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>enviar</button>
        </form>
        <script>
            let clientName = prompt("Digite seu nome", "");
            var ws = new WebSocket(`ws://4.tcp.ngrok.io:16848/ws/${clientName}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var msg = document.getElementById('messageText')
                ws.send(msg.value)
                msg.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str, actual_connection: WebSocket):
        for connection in self.active_connections:
            if connection != actual_connection:
                await connection.send_text(message)


manager = ConnectionManager()


@api.get('/')
async def get():
    return HTMLResponse(html)


@api.websocket('/ws/{client_name}')
async def websocket_endpoint(websocket: WebSocket, client_name: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f'>>Você: {data}', websocket)
            await manager.broadcast(f'>>{client_name}: {data}', websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f">>{client_name} saiu do chat!!")

if __name__ == '__main__':
    uvicorn.run("main:api", host="127.0.0.1", port=5000, log_level="info", reload=True)