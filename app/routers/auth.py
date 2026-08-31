from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.database import get_db
from app import models, schemas
from app.security import create_access_token
from app.deps import get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=schemas.TokenResponse)
def google_login(payload: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        idinfo = google_id_token.verify_oauth2_token(
            payload.id_token, google_requests.Request(), settings.google_client_id
        )
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_id = idinfo["sub"]
    email = idinfo.get("email")
    name = idinfo.get("name", email)
    avatar_url = idinfo.get("picture")

    user = db.query(models.User).filter(models.User.google_id == google_id).first()
    if not user:
        user = models.User(
            google_id=google_id, email=email, name=name, avatar_url=avatar_url
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return schemas.TokenResponse(access_token=token)


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout():
    # Stateless JWT: client discards the token. Endpoint kept for API symmetry.
    return {"detail": "Logged out"}
