from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.deps import get_current_user
from app.gemini import ask_gemini

router = APIRouter(prefix="/ai", tags=["ai"])


def _build_context(db: Session, user: models.User) -> str:
    tasks = (
        db.query(models.Task)
        .filter(models.Task.user_id == user.id, models.Task.status != models.TaskStatus.done)
        .order_by(models.Task.priority.desc())
        .limit(10)
        .all()
    )
    if not tasks:
        return "The user currently has no open tasks."
    lines = [f"- {t.title} (priority: {t.priority.value}, status: {t.status.value})" for t in tasks]
    return "The user's current open tasks:\n" + "\n".join(lines)


@router.post("/chat", response_model=schemas.AIChatOut)
def chat(
    payload: schemas.AIChatRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    context = _build_context(db, current_user)
    try:
        response_text = ask_gemini(payload.prompt, context)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    chat_row = models.AIChat(
        user_id=current_user.id, prompt=payload.prompt, response=response_text
    )
    db.add(chat_row)
    db.commit()
    db.refresh(chat_row)
    return chat_row


@router.get("/history", response_model=list[schemas.AIChatOut])
def history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.AIChat)
        .filter(models.AIChat.user_id == current_user.id)
        .order_by(models.AIChat.created_at.asc())
        .all()
    )


@router.delete("/history/{chat_id}")
def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    chat_row = (
        db.query(models.AIChat)
        .filter(models.AIChat.id == chat_id, models.AIChat.user_id == current_user.id)
        .first()
    )
    if not chat_row:
        raise HTTPException(status_code=404, detail="Chat entry not found")
    db.delete(chat_row)
    db.commit()
    return {"detail": "Chat entry deleted"}
