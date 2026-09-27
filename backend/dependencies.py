from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from backend.database import get_supabase
from backend.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente.")

    try:
        payload = decode_access_token(credentials.credentials)
    except HTTPException:
        raise
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.") from exc

    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sem usuário válido.")

    user_result = get_supabase().table("usuarios").select("*").eq("email", email).limit(1).execute()
    if not user_result.data:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado.")

    return user_result.data[0]


async def require_admin(current_user=Depends(get_current_user)):
    tipo = (current_user.get("tipo_usuario") or "").upper()
    if tipo not in {"ADM", "ADMIN"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso restrito ao administrador.")
    return current_user
