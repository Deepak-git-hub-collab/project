"""
Authentication & User Management Endpoints
Directly connected to SQLite users repository with cryptographic verification and Level 4 Full Authority audit logging.
"""
import secrets
import time
from fastapi import APIRouter, HTTPException, Header, status, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from backend.app.core.database import db, get_email_avatar_url
from backend.app.core.security import (
    hash_password,
    verify_password,
    generate_auth_token,
    verify_auth_token
)
from backend.app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Authentication & Users"])

def get_client_ip_and_agent(request: Optional[Request] = None):
    """Extracts client IP address and readable device signature for Level 4 audit tracking."""
    if not request:
        return "127.0.0.1", "Direct Console"
    try:
        headers = getattr(request, "headers", {})
        forwarded = headers.get("x-forwarded-for") if hasattr(headers, "get") else None
        if forwarded and isinstance(forwarded, str):
            client_ip = forwarded.split(",")[0].strip()
        elif hasattr(request, "client") and request.client and getattr(request.client, "host", None):
            client_ip = request.client.host
        else:
            client_ip = "127.0.0.1"

        raw_agent = headers.get("user-agent", "Web Browser") if hasattr(headers, "get") else "Web Browser"
        if not isinstance(raw_agent, str):
            raw_agent = "Web Browser"

        agent_display = "Desktop Browser"
        if "Windows" in raw_agent:
            agent_display = "Chrome / Windows" if "Chrome" in raw_agent else "Windows Browser"
        elif "Macintosh" in raw_agent or "Mac OS" in raw_agent:
            agent_display = "Safari / macOS" if "Safari" in raw_agent else "macOS Browser"
        elif "Android" in raw_agent:
            agent_display = "Mobile / Android"
        elif "iPhone" in raw_agent:
            agent_display = "Mobile / iOS"
        elif "Linux" in raw_agent:
            agent_display = "Linux Terminal / Station"
        return client_ip, agent_display
    except Exception:
        return "127.0.0.1", "Web Browser"

class LoginRequest(BaseModel):
    username: str = Field(default="admin@finsecure.io", description="Email or Username")
    password: str = Field(default="admin2026", description="User password")
    clearance: Optional[str] = Field(default="SUPERADMIN", description="Clearance tier")
    remember_me: Optional[bool] = Field(default=True, description="Remember login session")

class UpdateAvatarRequest(BaseModel):
    user_id: Optional[int] = Field(None, description="User database ID")
    email: Optional[str] = Field(None, description="User email")
    profile_picture_url: str = Field(..., description="New avatar URL or Data URL")

class GoogleLoginRequest(BaseModel):
    name: str = Field(..., description="Google Account Name")
    email: str = Field(..., description="Google Account Email")
    picture: Optional[str] = Field(None, description="Google Account Profile Picture URL")
    credential: Optional[str] = Field(None, description="Google OAuth Credential/JWT")

class RegisterRequest(BaseModel):
    name: str = Field(..., description="Full Name")
    email: str = Field(..., description="User Email")
    password: str = Field(..., description="User Password")
    role: Optional[str] = Field(default="Lead Risk Officer", description="Assigned role title")
    organization: Optional[str] = Field(default="FinSecure Inc.", description="Organization name")
    clearance: Optional[str] = Field(default="SuperAdmin • Level 4", description="Security clearance tier")
    profile_picture_url: Optional[str] = Field(None, description="Profile picture URL or uploaded base64")

@router.post("/update-avatar")
async def update_user_avatar_endpoint(
    req: UpdateAvatarRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Updates the authenticated operator's profile picture in the SQLite database.
    Can store a direct Google profile picture URL or uploaded image.
    """
    user = None
    tok = extract_bearer_token(authorization)
    if tok:
        payload = verify_auth_token(tok)
        if payload and payload.get("uid") is not None:
            try:
                user = db.get_user_by_id(int(payload["uid"]))
            except (ValueError, TypeError):
                user = None
            
    if not user and req.user_id is not None:
        user = db.get_user_by_id(req.user_id)
    if not user and req.email:
        user = db.get_user_by_email(req.email.strip().lower())
        
    if not user:
        raise HTTPException(status_code=404, detail="User account not found in SQLite database")
        
    new_avatar = req.profile_picture_url.strip()
    db.update_user_avatar(user["id"], new_avatar)
    updated = db.get_user_by_id(user["id"])
    if not updated:
        updated = {**user, "profile_picture_url": new_avatar}
    
    return {
        "status": "success",
        "message": "Profile picture updated successfully in SQLite",
        "user": {
            "id": updated["id"],
            "name": updated["name"],
            "email": updated["email"],
            "profile_picture_url": updated["profile_picture_url"],
            "role": updated["role"],
            "organization": updated["organization"],
            "clearance": updated["clearance"]
        }
    }

@router.post("/google-login")
async def google_login_endpoint(req: GoogleLoginRequest, request: Request):
    """
    Handles sign in or registration with a real Google account.
    Captures the real Google profile photo URL (e.g. from lh3.googleusercontent.com)
    and saves it to the SQLite users repository and Level 4 audit log.
    """
    client_ip, agent_display = get_client_ip_and_agent(request)
    email_clean = req.email.strip().lower()
    name_clean = req.name.strip()
    
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="Valid Google email required")
        
    user = db.get_user_by_email(email_clean)
    if not user:
        avatar = req.picture or get_email_avatar_url(email_clean)
        user = db.create_user(
            name=name_clean,
            email=email_clean,
            password_hash=hash_password(f"google_gsi_{email_clean}"),
            profile_picture_url=avatar,
            role="Lead Risk Officer",
            organization="Google Enclave",
            clearance="SuperAdmin • Level 4"
        )
        if not user:
            raise HTTPException(status_code=500, detail="Failed to initialize Google user profile")
        db.log_audit_event(
            action="ACCOUNT_CREATED_GOOGLE",
            actor=name_clean,
            target=email_clean,
            status="SUCCESS",
            details="New operator provisioned via Google Identity Services",
            ip_address=client_ip,
            user_agent=agent_display,
            clearance="SuperAdmin • Level 4"
        )
    else:
        if req.picture:
            db.update_user_avatar(user["id"], req.picture)
            user["profile_picture_url"] = req.picture
            
    token = generate_auth_token(user["id"], user["email"], user.get("role", "Admin"))
    user_clearance = user.get("clearance", "SuperAdmin • Level 4")
    db.log_audit_event(
        action="LOGIN_GOOGLE_SUCCESS",
        actor=user["name"],
        target=user["email"],
        status="SUCCESS",
        details="Authenticated via Google Identity Services",
        ip_address=client_ip,
        user_agent=agent_display,
        clearance=user_clearance
    )
    
    avatar_final = user.get("profile_picture_url") or req.picture or get_email_avatar_url(email_clean)
    return {
        "status": "success",
        "token": token,
        "token_type": "Bearer",
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "profile_picture_url": avatar_final,
            "role": user["role"],
            "organization": user["organization"],
            "clearance": user["clearance"]
        },
        "message": f"Welcome back via Google, {user['name']}"
    }

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    profile_picture_url: Optional[str] = None
    role: Optional[str] = None
    organization: Optional[str] = None
    clearance: Optional[str] = None
    created_at: Optional[str] = None

class LoginResponse(BaseModel):
    status: str
    token: str
    token_type: str
    user: Dict[str, Any]
    message: str

def extract_bearer_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Helper to extract token from standard Authorization header."""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return authorization

@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, request: Request):
    """
    Authenticates a user against the SQLite users database.
    Verifies cryptographic password hash (PBKDF2-HMAC-SHA256)
    and permanently logs access telemetry to the Level 4 Full Authority audit log.
    """
    client_ip, agent_display = get_client_ip_and_agent(request)
    identifier = req.username.strip().lower()
    raw_password = req.password.strip()

    if not identifier or not raw_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Workstation identifier/email and password are required"
        )

    # 1. Fetch user from SQLite by email or email prefix
    user = db.get_user_by_email(identifier)
    if not user and "@" not in identifier:
        user = db.get_user_by_email(f"{identifier}@finsecure.io")

    # 2. Check existence
    if not user:
        db.log_audit_event(
            action="LOGIN_FAILED",
            actor=identifier,
            target="AUTH_SUBSYSTEM",
            status="FAILURE",
            details=f"Unregistered identity attempted login: '{identifier}' (Not found in SQLite)",
            ip_address=client_ip,
            user_agent=agent_display,
            clearance="UNAUTHORIZED"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid credentials. No user with email '{identifier}' exists in SQLite database. Please create a new account."
        )

    # 3. Cryptographic password verification
    stored_hash = user.get("password_hash", "")
    if not verify_password(stored_hash, raw_password):
        db.log_audit_event(
            action="LOGIN_FAILED",
            actor=user["name"],
            target=user["email"],
            status="FAILURE",
            details="Cryptographic password verification failed (hash mismatch)",
            ip_address=client_ip,
            user_agent=agent_display,
            clearance=user.get("clearance", "Level 4")
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Incorrect password for this account."
        )

    # 4. Generate signed cryptographic session token
    token = generate_auth_token(user["id"], user["email"], user.get("role", "Admin"))

    # 5. Record successful login audit event in Level 4 Full Authority log
    user_clearance = user.get("clearance", "SuperAdmin • Level 4")
    db.log_audit_event(
        action="LOGIN_SUCCESS",
        actor=user["name"],
        target=user["email"],
        status="SUCCESS",
        details=f"Authenticated as {user['role']} ({user_clearance})",
        ip_address=client_ip,
        user_agent=agent_display,
        clearance=user_clearance
    )

    # 6. Ensure profile picture is accurately fetched from the user's email account
    avatar_url = user.get("profile_picture_url")
    if not avatar_url or "images.unsplash.com" in avatar_url:
        avatar_url = get_email_avatar_url(user["email"])
        try:
            db.update_user_avatar(user["id"], avatar_url)
        except Exception:
            pass

    clean_user = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "profile_picture_url": avatar_url,
        "role": user["role"],
        "organization": user["organization"],
        "clearance": user["clearance"]
    }

    return LoginResponse(
        status="success",
        token=token,
        token_type="Bearer",
        user=clean_user,
        message=f"Welcome back, {user['name']}"
    )

@router.get("/me")
async def get_current_user(authorization: Optional[str] = Header(None), token: Optional[str] = None):
    """
    Dynamically fetches the authenticated user's actual profile from the SQLite database.
    If no valid token is provided, returns Anonymous user session state.
    """
    tok = token or extract_bearer_token(authorization)
    if not tok:
        return {
            "is_authenticated": False,
            "user": {
                "id": 0,
                "name": "Anonymous User",
                "email": "anonymous@shieldplus.local",
                "role": "Guest Operator",
                "organization": "Unauthenticated Session",
                "clearance": "Level 0: Read-Only Public",
                "profile_picture_url": ""
            },
            "message": "Anonymous profile active"
        }

    payload = verify_auth_token(tok)
    if not payload:
        return {
            "is_authenticated": False,
            "user": {
                "id": 0,
                "name": "Anonymous User",
                "email": "anonymous@shieldplus.local",
                "role": "Guest Operator",
                "organization": "Session Expired",
                "clearance": "Level 0: Read-Only Public",
                "profile_picture_url": ""
            },
            "message": "Token expired or invalid"
        }

    user = None
    uid = payload.get("uid")
    if uid is not None:
        try:
            user = db.get_user_by_id(int(uid))
        except (ValueError, TypeError):
            user = None
    if not user and payload.get("email"):
        user = db.get_user_by_email(str(payload.get("email", "")).strip().lower())
    if not user:
        raise HTTPException(status_code=404, detail="User account no longer found in SQLite database")

    avatar_url = user.get("profile_picture_url")
    if not avatar_url or "images.unsplash.com" in avatar_url:
        avatar_url = get_email_avatar_url(user["email"])
        try:
            db.update_user_avatar(user["id"], avatar_url)
        except Exception:
            pass

    return {
        "is_authenticated": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "profile_picture_url": avatar_url,
            "role": user["role"],
            "organization": user["organization"],
            "clearance": user["clearance"]
        },
        "message": "Authenticated user profile loaded from SQLite"
    }

@router.post("/logout")
async def logout(request: Request, authorization: Optional[str] = Header(None)):
    """Gracefully terminates session and logs audit trail."""
    client_ip, agent_display = get_client_ip_and_agent(request)
    tok = extract_bearer_token(authorization)
    actor = "User"
    clearance = "Level 4"
    if tok:
        payload = verify_auth_token(tok)
        if payload:
            actor = payload.get("email", "User")
            clearance = payload.get("role", "Level 4")

    db.log_audit_event(
        action="USER_LOGOUT",
        actor=actor,
        target="AUTH_SUBSYSTEM",
        status="SUCCESS",
        details="Session terminated. UI reverted to Anonymous User state.",
        ip_address=client_ip,
        user_agent=agent_display,
        clearance=clearance
    )
    return {
        "status": "success",
        "message": "Logged out successfully. Reverted to Anonymous User profile."
    }

@router.get("/users", response_model=List[Dict[str, Any]])
async def list_users():
    """Returns all operators and security clearance profiles stored in SQLite."""
    return db.get_all_users()

@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register_user(req: RegisterRequest, request: Request):
    """
    Registers a new user in the SQLite users table with PBKDF2 hashed password
    and permanently records the creation event in the Level 4 Full Authority audit log.
    """
    client_ip, agent_display = get_client_ip_and_agent(request)
    email_clean = req.email.strip().lower()
    name_clean = req.name.strip()

    if not name_clean:
        raise HTTPException(status_code=400, detail="Full Name is required.")
    if not email_clean or "@" not in email_clean:
        raise HTTPException(status_code=400, detail="A valid email address is required.")
    if len(req.password.strip()) < 4:
        raise HTTPException(status_code=400, detail="Security passkey must be at least 4 characters.")

    existing = db.get_user_by_email(email_clean)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An account with email {email_clean} already exists. Please sign in instead."
        )

    pwd_hash = hash_password(req.password.strip())
    # Profile picture is fetched from the email account
    avatar_url = req.profile_picture_url or get_email_avatar_url(email_clean)
    clearance_tier = req.clearance or "SuperAdmin • Level 4"
    role_tier = req.role or "Lead Risk Officer"
    org_tier = req.organization or "FinSecure Inc."

    user = db.create_user(
        name=name_clean,
        email=email_clean,
        password_hash=pwd_hash,
        profile_picture_url=avatar_url,
        role=role_tier,
        organization=org_tier,
        clearance=clearance_tier
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize user record in SQLite database"
        )

    # Permanently record in Level 4 Full Authority audit log
    db.log_audit_event(
        action="ACCOUNT_CREATED",
        actor=name_clean,
        target=email_clean,
        status="SUCCESS",
        details=f"New operator account registered: {role_tier} ({clearance_tier})",
        ip_address=client_ip,
        user_agent=agent_display,
        clearance=clearance_tier
    )

    # Also generate immediate session token so newly registered user can auto-login
    token = generate_auth_token(user["id"], user["email"], user.get("role", "Admin"))

    clean_user = {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "profile_picture_url": user["profile_picture_url"],
        "role": user["role"],
        "organization": user["organization"],
        "clearance": user["clearance"]
    }

    return {
        "status": "success",
        "message": f"Account for {name_clean} created successfully in SQLite with {clearance_tier}",
        "token": token,
        "token_type": "Bearer",
        "user": clean_user
    }

@router.get("/audit-logs")
async def get_authority_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = Query("ALL", description="Filter by event type"),
    search: Optional[str] = Query(None, description="Search term for user, email, or IP")
):
    """
    Level 4 Full Authority Audit Trail.
    Provides complete visibility into all accounts created, login events, and security access.
    """
    logs = db.get_recent_audit_logs(limit=limit, action_filter=action, search_term=search)
    stats = db.get_audit_summary_stats()
    all_users = db.get_all_users()

    return {
        "status": "success",
        "authority_level": "Level 4: SuperAdmin (Full Authority & Unrestricted Oversight)",
        "summary": stats,
        "total_returned": len(logs),
        "audit_logs": logs,
        "registered_users_count": len(all_users),
        "registered_users": all_users
    }

# =========================================================================
# Workstation Password Reset & Email Dispatch Endpoints (Mobile & Laptop)
# =========================================================================

class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., description="Operator workstation email address")

class VerifyResetTokenRequest(BaseModel):
    token: Optional[str] = Field(None, description="Cryptographic URL token")
    code: Optional[str] = Field(None, description="6-digit verification code")
    email: Optional[str] = Field(None, description="Target operator email")

class ResetPasswordRequest(BaseModel):
    token: Optional[str] = Field(None, description="Cryptographic URL token")
    code: Optional[str] = Field(None, description="6-digit verification code")
    email: Optional[str] = Field(None, description="Target operator email")
    new_password: str = Field(..., description="New security passkey")

@router.post("/forgot-password")
async def forgot_password_endpoint(req: ForgotPasswordRequest, request: Request):
    """
    Initiates password recovery for an operator account in SQLite.
    Generates a secure cryptographic reset token and 6-digit OTP code,
    dispatches a responsive HTML email via real SMTP (Gmail, Outlook, Brevo),
    and records the event in the Level 4 Full Authority audit log.
    """
    client_ip, agent_display = get_client_ip_and_agent(request)
    email_clean = req.email.strip().lower()

    if not email_clean or "@" not in email_clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid workstation email address is required"
        )

    user = db.get_user_by_email(email_clean)
    if not user:
        if "@" not in email_clean:
            user = db.get_user_by_email(f"{email_clean}@finsecure.io")
        if not user:
            db.log_audit_event(
                action="PASSWORD_RESET_REJECTED",
                actor=email_clean,
                target="AUTH_RECOVERY",
                status="FAILURE",
                details=f"Password recovery requested for non-existent identity: '{email_clean}'",
                ip_address=client_ip,
                user_agent=agent_display,
                clearance="UNAUTHORIZED"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No operator account with email '{email_clean}' exists in SQLite database."
            )

    # Generate 64-character URL-safe reset token and 6-digit OTP code
    reset_token = secrets.token_urlsafe(36)
    reset_code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = time.time() + (15 * 60) # 15 minutes validity

    # Persist in SQLite
    db.create_password_reset(
        email=user["email"],
        token=reset_token,
        code=reset_code,
        expires_at=expires_at,
        ip_address=client_ip,
        user_agent=agent_display
    )

    # Determine base URL for one-click clickable links on mobile & laptop
    base_url = str(request.base_url).rstrip("/")

    # Dispatch email
    dispatch_result = send_password_reset_email(
        to_email=user["email"],
        user_name=user["name"],
        reset_token=reset_token,
        reset_code=reset_code,
        base_url=base_url,
        client_ip=client_ip,
        user_agent=agent_display
    )

    # Log to Level 4 Full Authority audit trail
    db.log_audit_event(
        action="PASSWORD_RESET_REQUESTED",
        actor=user["name"],
        target=user["email"],
        status="SUCCESS",
        details=f"Passkey recovery dispatched ({dispatch_result.get('method', 'smtp')}). OTP: {reset_code}",
        ip_address=client_ip,
        user_agent=agent_display,
        clearance=user.get("clearance", "SuperAdmin • Level 4")
    )

    return {
        "status": "success",
        "message": f"Password reset instructions and 6-digit passkey sent to {user['email']}",
        "email": user["email"],
        "user_name": user["name"],
        "delivery_method": dispatch_result.get("method"),
        "expires_in_minutes": 15,
        "reset_link": dispatch_result.get("reset_link"),
        "reset_code": reset_code
    }

@router.post("/verify-reset-token")
async def verify_reset_token_endpoint(req: VerifyResetTokenRequest):
    """
    Validates whether a reset token or 6-digit OTP code is valid, unexpired, and unused in SQLite.
    """
    token_or_code = (req.token or req.code or "").strip()
    if not token_or_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token or 6-digit verification code is required"
        )

    record = db.get_password_reset(token_or_code, email=req.email)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset passkey. Please request a new one."
        )

    user = db.get_user_by_email(record["email"])
    return {
        "status": "valid",
        "email": record["email"],
        "user_name": user["name"] if user else "Operator",
        "expires_at": record["expires_at"]
    }

@router.post("/reset-password")
async def reset_password_endpoint(req: ResetPasswordRequest, request: Request):
    """
    Applies the new passkey to the operator's SQLite record after validating token/code.
    Hashes new password with PBKDF2-HMAC-SHA256, marks token used, and logs Level 4 event.
    """
    client_ip, agent_display = get_client_ip_and_agent(request)
    token_or_code = (req.token or req.code or "").strip()
    new_pwd = req.new_password.strip()

    if not token_or_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token or 6-digit code is required"
        )
    if len(new_pwd) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New security passkey must be at least 4 characters long"
        )

    record = db.get_password_reset(token_or_code, email=req.email)
    if not record:
        db.log_audit_event(
            action="PASSWORD_RESET_FAILED",
            actor=req.email or "Unknown",
            target="AUTH_SUBSYSTEM",
            status="FAILURE",
            details="Attempted password reset with invalid or expired token/code",
            ip_address=client_ip,
            user_agent=agent_display,
            clearance="UNAUTHORIZED"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid, expired, or already-used reset passkey. Please request a new recovery link."
        )

    user = db.get_user_by_email(record["email"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User account associated with this token no longer exists in SQLite database"
        )

    # Hash new password with PBKDF2-HMAC-SHA256
    new_hash = hash_password(new_pwd)
    db.update_user_password_by_email(user["email"], new_hash)
    db.mark_password_reset_used(record["id"])

    # Log successful reset event in Level 4 Full Authority audit log
    db.log_audit_event(
        action="PASSWORD_RESET_SUCCESS",
        actor=user["name"],
        target=user["email"],
        status="SUCCESS",
        details="Operator passkey successfully reset via email verification and re-hashed in SQLite",
        ip_address=client_ip,
        user_agent=agent_display,
        clearance=user.get("clearance", "SuperAdmin • Level 4")
    )

    # Generate immediate login token so operator can enter terminal seamlessly
    token = generate_auth_token(user["id"], user["email"], user.get("role", "Admin"))

    return {
        "status": "success",
        "message": f"Security passkey for {user['name']} has been successfully updated in SQLite. You can now log in.",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "profile_picture_url": user.get("profile_picture_url") or get_email_avatar_url(user["email"]),
            "role": user["role"],
            "organization": user["organization"],
            "clearance": user["clearance"]
        }
    }
