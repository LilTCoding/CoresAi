"""
CoresAI Discord Authentication Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from typing import Optional
import jwt
from datetime import datetime, timedelta
from .discord_integration import oauth, bot
from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRATION, FRONTEND_URL

router = APIRouter()

def create_jwt_token(data: dict) -> str:
    """Create JWT token for user session"""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION)
    to_encode = data.copy()
    to_encode.update({"exp": expiration})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/auth/discord")
async def discord_auth():
    """Redirect to Discord OAuth"""
    return RedirectResponse(url=oauth.get_oauth_url())

@router.get("/auth/discord/callback")
async def discord_callback(code: str, request: Request):
    """Handle Discord OAuth callback"""
    try:
        # Get access token
        token_data = await oauth.get_access_token(code)
        access_token = token_data["access_token"]
        
        # Get user data
        user_data = await oauth.get_user_data(access_token)
        
        # Add user to Discord server
        added_to_guild = await oauth.add_to_guild(access_token, user_data["id"])
        
        # Create session token
        session_token = create_jwt_token({
            "user_id": user_data["id"],
            "username": user_data["username"],
            "email": user_data.get("email"),
            "discord_token": access_token
        })
        
        # Log successful authentication
        await bot.log_event(
            f"User {user_data['username']} ({user_data['id']}) authenticated successfully",
            level="info"
        )
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth-success?token={session_token}"
        )
        
    except Exception as e:
        await bot.log_event(
            f"Authentication failed: {str(e)}",
            level="error"
        )
        return RedirectResponse(
            url=f"{FRONTEND_URL}/auth-error"
        )

@router.get("/auth/user")
async def get_user(token: str):
    """Get current authenticated user"""
    try:
        # Verify token
        payload = verify_jwt_token(token)
        
        # Get fresh user data from Discord
        user_data = await oauth.get_user_data(payload["discord_token"])
        
        return {
            "user": {
                "id": user_data["id"],
                "username": user_data["username"],
                "email": user_data.get("email"),
                "avatar": user_data.get("avatar"),
                "discriminator": user_data["discriminator"]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/auth/logout")
async def logout(token: str):
    """Logout user"""
    try:
        # Verify token
        payload = verify_jwt_token(token)
        
        # Log event
        await bot.log_event(
            f"User {payload['username']} logged out",
            level="info"
        )
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) 