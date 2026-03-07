import logging
import asyncio
from fastapi import FastAPI, Request, HTTPException, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
import websockets
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

# Configuration for backend services
SERVICES = {
    "symbol": "http://localhost:8000",
    "auth": "http://localhost:8001",
    "shape": "http://localhost:8003",
    "number": "http://localhost:8004",
}

# WS Mappings (Websocket uses ws:// instead of http://)
WS_SERVICES = {
    "symbol": "ws://localhost:8000",
    "auth": "ws://localhost:8001",
    "shape": "ws://localhost:8003",
    "number": "ws://localhost:8004",
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup global client with high connection pool
    limits = httpx.Limits(max_connections=100, max_keepalive_connections=20)
    app.state.client = httpx.AsyncClient(timeout=30.0, limits=limits)
    yield
    # Cleanup
    await app.state.client.aclose()

app = FastAPI(title="Ganitha Mithura Gateway", lifespan=lifespan)

# Allow CORS for flutter app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WEBSOCKET PROXY ---
@app.websocket("/{service_name}/{path:path}")
async def websocket_proxy(service_name: str, path: str, websocket: WebSocket):
    if service_name not in WS_SERVICES:
        await websocket.close(code=1008)
        return

    target_ws_base = WS_SERVICES[service_name].rstrip("/")
    target_path = path if path.startswith("/") else f"/{path}"
    target_ws_url = f"{target_ws_base}{target_path}"
    
    # Preserve query params
    query_string = str(websocket.query_params)
    if query_string:
        target_ws_url = f"{target_ws_url}?{query_string}"

    logger.info(f"🆕 Proxying WebSocket: {websocket.url} -> {target_ws_url}")
    
    await websocket.accept()

    try:
        async with websockets.connect(target_ws_url) as target_ws:
            # Task to forward messages from client to target
            async def forward_to_target():
                try:
                    while True:
                        # Receive message from client (FastAPI WebSocket)
                        data = await websocket.receive()
                        if data["type"] == "websocket.receive":
                            if "text" in data:
                                await target_ws.send(data["text"])
                            elif "bytes" in data:
                                await target_ws.send(data["bytes"])
                        elif data["type"] == "websocket.disconnect":
                            break
                except Exception as e:
                    logger.debug(f"Forward to target ended: {e}")

            # Task to forward messages from target to client
            async def forward_to_client():
                try:
                    async for message in target_ws:
                        if isinstance(message, str):
                            await websocket.send_text(message)
                        else:
                            await websocket.send_bytes(message)
                except Exception as e:
                    logger.debug(f"Forward to client ended: {e}")

            # Run both tasks and wait for one to complete
            done, pending = await asyncio.wait(
                [asyncio.create_task(forward_to_target()), 
                 asyncio.create_task(forward_to_client())],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # Cancel remaining tasks
            for task in pending:
                task.cancel()

    except Exception as e:
        logger.error(f"WebSocket Proxy Error for {target_ws_url}: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass
        logger.info(f"🛑 WebSocket Proxy Closed for {target_ws_url}")

# --- HTTP PROXY ---
@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

    base_url = SERVICES[service_name].rstrip("/")
    target_path = path if path.startswith("/") else f"/{path}"
    target_url = f"{base_url}{target_path}"
    
    # Forward all headers except host
    headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]}
    
    # Add ngrok bypass header just in case it's forwarded
    headers["ngrok-skip-browser-warning"] = "true"
    
    # Process body
    content = await request.body()
    
    # Process query params
    params = dict(request.query_params)

    try:
        # Perform the proxy request
        response = await app.state.client.request(
            method=request.method,
            url=target_url,
            content=content,
            headers=headers,
            params=params,
            follow_redirects=True
        )
        
        # Log results for debugging
        logger.info(f"Proxying: {request.method} {request.url.path} -> {target_url} [{response.status_code}]")
        
        # Return the backend response exactly as is
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers={k: v for k, v in response.headers.items() if k.lower() not in ["content-length", "content-encoding"]}
        )
    except httpx.ConnectError:
        logger.error(f"Service {service_name} at {target_url} is offline")
        raise HTTPException(status_code=502, detail=f"Service {service_name} is offline")
    except Exception as e:
        logger.error(f"Gateway error to {target_url}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def gateway_health():
    return {"status": "gateway_up"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
