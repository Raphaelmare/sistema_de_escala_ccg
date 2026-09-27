from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_supabase
from backend.dependencies import require_admin
from backend.schemas.usuarios import UsuarioCreate

router = APIRouter(prefix="/professores", tags=["professores"])


@router.get("")
def list_professores(current_user=Depends(require_admin)):
    data = get_supabase().table("usuarios").select("*").eq("tipo_usuario", "PROFESSOR").order("id").execute()
    return data.data or []


@router.get("/{usuario_id}")
def get_professor(usuario_id: int, current_user=Depends(require_admin)):
    data = get_supabase().table("usuarios").select("*").eq("id", usuario_id).single().execute()
    if not data.data:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")
    return data.data


@router.post("")
def create_professor(payload: UsuarioCreate, current_user=Depends(require_admin)):
    if payload.tipo_usuario.upper() != "PROFESSOR":
        payload.tipo_usuario = "PROFESSOR"

    if payload.sala_id is not None:
        sala = get_supabase().table("salas").select("id").eq("id", payload.sala_id).limit(1).execute().data or []
        if not sala:
            raise HTTPException(status_code=400, detail="Sala informada não existe.")

    existing = get_supabase().table("usuarios").select("id").eq("email", payload.email.lower()).execute()
    if existing.data:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado.")

    item = {
        "nome": payload.nome,
        "email": payload.email.lower(),
        "senha_hash": __import__("backend.security", fromlist=["hash_password"]).hash_password(payload.password),
        "telefone": payload.telefone,
        "tipo_usuario": "PROFESSOR",
        "sala_id": payload.sala_id,
        "ativo": True,
    }
    created = get_supabase().table("usuarios").insert(item).execute()
    return {"status": "ok", "professor": created.data[0]}


@router.put("/{usuario_id}")
def update_professor(usuario_id: int, payload: dict, current_user=Depends(require_admin)):
    data = dict(payload)

    if "email" in data and data["email"]:
        data["email"] = data["email"].lower()

    senha = data.pop("senha", None)
    if senha is None:
        senha = data.pop("password", None)
    if senha is not None and str(senha).strip():
        data["senha_hash"] = __import__("backend.security", fromlist=["hash_password"]).hash_password(str(senha))

    if "senha_hash" in data and not data["senha_hash"]:
        data.pop("senha_hash")

    updated = get_supabase().table("usuarios").update(data).eq("id", usuario_id).execute()
    return {"status": "ok", "professor": updated.data[0] if updated.data else None}


@router.patch("/{usuario_id}/ativar")
def ativar_professor(usuario_id: int, current_user=Depends(require_admin)):
    updated = get_supabase().table("usuarios").update({"ativo": True}).eq("id", usuario_id).execute()
    return {"status": "ok", "professor": updated.data[0] if updated.data else None}


@router.patch("/{usuario_id}/inativar")
def inativar_professor(usuario_id: int, current_user=Depends(require_admin)):
    updated = get_supabase().table("usuarios").update({"ativo": False}).eq("id", usuario_id).execute()
    return {"status": "ok", "professor": updated.data[0] if updated.data else None}


@router.delete("/{usuario_id}")
def delete_professor(usuario_id: int, current_user=Depends(require_admin)):
    get_supabase().table("usuarios").delete().eq("id", usuario_id).execute()
    return {"status": "ok"}
