"""
Monitoring Routes
Real-time monitoring and WebSocket endpoints for task observation.
"""

import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Dict, List
from datetime import datetime
from ..services.task_manager import task_manager
from ..services.resource_manager import resource_manager

router = APIRouter(prefix="/api/monitor", tags=["Monitoring"])


# ============== DASHBOARD DATA ==============

@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data."""
    task_stats = task_manager.get_statistics()
    resource_stats = resource_manager.get_all_statistics()
    
    # Get recent tasks
    all_tasks = task_manager.get_all_tasks()
    recent_tasks = all_tasks[:10]  # Last 10 tasks
    
    # Get active tasks
    active_tasks = [t for t in all_tasks if t.status.value == "running"]
    
    # Get recent errors across all tasks
    recent_errors = []
    for task in all_tasks:
        for error in task.errors[-5:]:  # Last 5 errors per task
            recent_errors.append({
                "task_id": task.id,
                "task_name": task.name,
                "error": error.dict()
            })
    recent_errors.sort(key=lambda x: x["error"]["timestamp"], reverse=True)
    recent_errors = recent_errors[:20]  # Limit to 20 most recent
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "tasks": task_stats,
        "resources": resource_stats,
        "recent_tasks": [t.dict() for t in recent_tasks],
        "active_tasks": [t.dict() for t in active_tasks],
        "recent_errors": recent_errors
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "task_manager": "operational",
            "resource_manager": "operational"
        }
    }


# ============== SERVER-SENT EVENTS ==============

async def event_generator():
    """Generate server-sent events for real-time updates."""
    queue = await task_manager.subscribe("*")
    try:
        while True:
            try:
                # Wait for event with timeout
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event, default=str)}\n\n"
            except asyncio.TimeoutError:
                # Send heartbeat
                yield f"data: {json.dumps({'event': 'heartbeat', 'timestamp': datetime.utcnow().isoformat()})}\n\n"
    except asyncio.CancelledError:
        task_manager.unsubscribe("*", queue)
        raise


@router.get("/events")
async def stream_events():
    """Stream task events via Server-Sent Events."""
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ============== WEBSOCKET ==============

class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass


ws_manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time bidirectional communication."""
    await ws_manager.connect(websocket)
    queue = await task_manager.subscribe("*")
    
    try:
        # Create tasks for both receiving and sending
        async def send_updates():
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    await websocket.send_json(event)
                except asyncio.TimeoutError:
                    await websocket.send_json({
                        "event": "heartbeat",
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        async def receive_messages():
            while True:
                data = await websocket.receive_json()
                # Handle incoming commands
                if data.get("action") == "subscribe":
                    task_id = data.get("task_id")
                    # Additional subscription logic here
                    await websocket.send_json({
                        "event": "subscribed",
                        "task_id": task_id
                    })
                elif data.get("action") == "get_dashboard":
                    dashboard = await get_dashboard_data()
                    await websocket.send_json({
                        "event": "dashboard",
                        "data": dashboard
                    })
        
        # Run both tasks concurrently
        send_task = asyncio.create_task(send_updates())
        receive_task = asyncio.create_task(receive_messages())
        
        done, pending = await asyncio.wait(
            [send_task, receive_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        for task in pending:
            task.cancel()
            
    except WebSocketDisconnect:
        pass
    finally:
        ws_manager.disconnect(websocket)
        task_manager.unsubscribe("*", queue)


@router.websocket("/ws/task/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for monitoring a specific task."""
    task = task_manager.get_task(task_id)
    if not task:
        await websocket.close(code=4004, reason="Task not found")
        return
    
    await websocket.accept()
    queue = await task_manager.subscribe(task_id)
    
    # Send initial task state
    await websocket.send_json({
        "event": "initial_state",
        "task": task.dict()
    })
    
    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json(event)
            except asyncio.TimeoutError:
                await websocket.send_json({
                    "event": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        pass
    finally:
        task_manager.unsubscribe(task_id, queue)
