from fastapi import APIRouter, HTTPException

from backend.database import get_supabase
from backend.security import create_access_token, hash_password, verify_password
from backend.schemas.auth import LoginRequest, TokenResponse
from backend.schemas.usuarios import UsuarioCreate

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    supabase = get_supabase()
    try:
        result = supabase.table("usuarios").select("*").eq("email", payload.email.lower()).limit(1).execute()
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Erro ao consultar usuário.") from exc

    if not result.data:
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    usuario = result.data[0]
    if not usuario.get("ativo", False):
        raise HTTPException(status_code=401, detail="Usuário inativo.")

    if not verify_password(payload.password, usuario.get("senha_hash") or ""):
        raise HTTPException(status_code=401, detail="Credenciais inválidas.")

    token = create_access_token(usuario["email"], {"tipo_usuario": usuario.get("tipo_usuario", "PROFESSOR")})
    return {
        "access_token": token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.get("id"),
            "nome": usuario.get("nome"),
            "email": usuario.get("email"),
            "tipo_usuario": usuario.get("tipo_usuario"),
            "ativo": usuario.get("ativo"),
        },
    }


@router.post("/register")
def register(payload: UsuarioCreate):
    supabase = get_supabase()
    normalized_email = payload.email.lower()

    existing = supabase.table("usuarios").select("id").eq("email", normalized_email).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    usuario = {
        "nome": payload.nome,
        "email": normalized_email,
        "senha_hash": hash_password(payload.password),
        "telefone": payload.telefone,
        "tipo_usuario": payload.tipo_usuario.upper(),
        "ativo": True,
    }

    created = supabase.table("usuarios").insert(usuario).execute()
    if not created.data:
        raise HTTPException(status_code=400, detail="Não foi possível criar o usuário.")

    return {"status": "ok", "usuario": created.data[0]}
