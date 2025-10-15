from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Dict, Set
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.security import decode_access_token
from src.models.conversation import Conversation, Message
from src.models.user import User

router = APIRouter()


class ConnectionManager:
    """مدیریت اتصالات WebSocket"""
    
    def __init__(self):
        # {conversation_id: {user_id: websocket}}
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, conversation_id: str, user_id: str):
        """اتصال کاربر به مکالمه"""
        await websocket.accept()
        
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = {}
        
        self.active_connections[conversation_id][user_id] = websocket
        
        # ارسال پیام خوش‌آمدگویی
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "conversation_id": conversation_id,
            "message": "Successfully connected to chat"
        })
        
        print(f"✅ User {user_id} connected to conversation {conversation_id}")
    
    def disconnect(self, conversation_id: str, user_id: str):
        """قطع اتصال کاربر"""
        if conversation_id in self.active_connections:
            if user_id in self.active_connections[conversation_id]:
                del self.active_connections[conversation_id][user_id]
                print(f"❌ User {user_id} disconnected from conversation {conversation_id}")
            
            # حذف conversation اگر دیگر کاربری متصل نیست
            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]
                print(f"🗑️  Conversation {conversation_id} removed (no active connections)")
    
    async def broadcast_to_conversation(
        self,
        conversation_id: str,
        message: dict,
        exclude_user: str = None
    ):
        """ارسال پیام به تمام کاربران یک مکالمه"""
        if conversation_id not in self.active_connections:
            return
        
        disconnected_users = []
        
        for user_id, websocket in self.active_connections[conversation_id].items():
            # عدم ارسال به کاربر فرستنده (اختیاری)
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # حذف کاربران قطع شده
        for user_id in disconnected_users:
            self.disconnect(conversation_id, user_id)
    
    def get_active_users(self, conversation_id: str) -> int:
        """دریافت تعداد کاربران فعال در مکالمه"""
        if conversation_id in self.active_connections:
            return len(self.active_connections[conversation_id])
        return 0


# Manager instance
manager = ConnectionManager()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint برای چت Real-time"""
    
    # احراز هویت
    if not token:
        await websocket.close(code=1008, reason="Authentication required")
        return
    
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008, reason="Invalid token")
            return
    except Exception as e:
        await websocket.close(code=1008, reason=f"Auth error: {str(e)}")
        return
    
    # بررسی وجود conversation
    try:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            await websocket.close(code=1003, reason="Conversation not found")
            return
        
        # بررسی دسترسی کاربر
        if conversation.user_id != user_id:
            await websocket.close(code=1003, reason="Access denied")
            return
    except Exception as e:
        print(f"Database error: {e}")
        await websocket.close(code=1011, reason="Server error")
        return
    
    # اتصال کاربر
    await manager.connect(websocket, conversation_id, user_id)
    
    try:
        while True:
            # دریافت پیام از کلاینت
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "chat":
                # ایجاد پیام جدید در database
                new_message = Message(
                    conversation_id=conversation_id,
                    role="user",
                    content=message_data.get("content"),
                    metadata=json.dumps(message_data.get("metadata", {}))
                )
                db.add(new_message)
                await db.commit()
                await db.refresh(new_message)
                
                # ارسال پیام کاربر به همه
                await manager.broadcast_to_conversation(
                    conversation_id,
                    {
                        "type": "message",
                        "message": {
                            "id": str(new_message.id),
                            "conversation_id": conversation_id,
                            "role": "user",
                            "content": new_message.content,
                            "created_at": new_message.created_at.isoformat() if new_message.created_at else None,
                        }
                    }
                )
                
                # پردازش با AI (async)
                asyncio.create_task(
                    process_ai_response(conversation_id, str(new_message.id), user_id, db)
                )
            
            elif message_type == "typing":
                # ارسال نمایش typing به سایرین
                await manager.broadcast_to_conversation(
                    conversation_id,
                    {
                        "type": "typing",
                        "user_id": user_id,
                        "is_typing": message_data.get("is_typing", False)
                    },
                    exclude_user=user_id
                )
            
            elif message_type == "ping":
                # پاسخ به ping برای حفظ اتصال
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": message_data.get("timestamp")
                })
    
    except WebSocketDisconnect:
        manager.disconnect(conversation_id, user_id)
        # اطلاع به سایرین
        await manager.broadcast_to_conversation(
            conversation_id,
            {
                "type": "user_disconnected",
                "user_id": user_id
            }
        )
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(conversation_id, user_id)


async def process_ai_response(
    conversation_id: str,
    user_message_id: str,
    user_id: str,
    db: AsyncSession
):
    """پردازش پاسخ AI به صورت async"""
    from src.services.ai_service import AIService
    
    try:
        # گرفتن پیام کاربر
        result = await db.execute(
            select(Message).where(Message.id == user_message_id)
        )
        user_message = result.scalar_one_or_none()
        
        if not user_message:
            return
        
        # ارسال notification شروع پردازش
        await manager.broadcast_to_conversation(
            conversation_id,
            {
                "type": "processing",
                "status": "analyzing",
                "message": "در حال تحلیل درخواست شما..."
            }
        )
        
        # تحلیل و تولید پاسخ
        ai_service = AIService()
        analysis = await ai_service.analyze_prompt(user_message.content)
        
        # ایجاد پیام AI
        ai_message = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=json.dumps(analysis, ensure_ascii=False),
            metadata=json.dumps({"analysis": True, "type": "prompt_analysis"})
        )
        db.add(ai_message)
        await db.commit()
        await db.refresh(ai_message)
        
        # ارسال پاسخ AI از طریق WebSocket
        await manager.broadcast_to_conversation(
            conversation_id,
            {
                "type": "message",
                "message": {
                    "id": str(ai_message.id),
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": ai_message.content,
                    "created_at": ai_message.created_at.isoformat() if ai_message.created_at else None,
                }
            }
        )
        
        # ارسال notification اتمام پردازش
        await manager.broadcast_to_conversation(
            conversation_id,
            {
                "type": "processing",
                "status": "completed",
                "message": "تحلیل با موفقیت انجام شد!"
            }
        )
        
    except Exception as e:
        print(f"Error processing AI response: {e}")
        
        # ارسال پیام خطا
        await manager.broadcast_to_conversation(
            conversation_id,
            {
                "type": "error",
                "message": "خطا در پردازش پیام. لطفاً دوباره تلاش کنید.",
                "error": str(e)
            }
        )


@router.get("/ws/stats")
async def get_websocket_stats():
    """دریافت آمار WebSocket connections"""
    total_conversations = len(manager.active_connections)
    total_users = sum(
        len(users) for users in manager.active_connections.values()
    )
    
    return {
        "active_conversations": total_conversations,
        "active_users": total_users,
        "connections": {
            conv_id: len(users)
            for conv_id, users in manager.active_connections.items()
        }
    }
