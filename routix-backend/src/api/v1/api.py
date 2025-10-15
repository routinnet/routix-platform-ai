from fastapi import APIRouter

from src.api.v1.endpoints import auth, chat, generations, users, files, websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(generations.router, tags=["generations"])
api_router.include_router(websocket.router, tags=["websocket"])
