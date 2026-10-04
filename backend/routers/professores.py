import logging

from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_supabase
from backend.dependencies import require_admin
from backend.schemas.usuarios import UsuarioCreate, UsuarioUpdate

router = APIRouter(prefix="/professores", tags=["professores"])
logger = logging.getLogger(__name__)


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
def update_professor(usuario_id: int, payload: UsuarioUpdate, current_user=Depends(require_admin)):
    data = payload.model_dump(exclude_unset=True)

    senha = data.pop("senha", None)
    password = data.pop("password", None)
    senha = password if password is not None else senha
    if senha is not None and str(senha).strip():
        try:
            data["senha_hash"] = __import__("backend.security", fromlist=["hash_password"]).hash_password(str(senha))
        except Exception as exc:
            logger.exception("Falha ao gerar hash da senha do professor id=%s", usuario_id)
            raise HTTPException(status_code=500, detail="Não foi possível processar a senha. Consulte os logs do Render.") from exc

    if not data:
        raise HTTPException(status_code=400, detail="Informe ao menos um campo para atualizar.")

    for field in ("nome", "email", "tipo_usuario", "ativo"):
        if field in data and data[field] is None:
            raise HTTPException(status_code=400, detail=f"O campo {field} não pode ficar vazio.")

    if "nome" in data:
        data["nome"] = data["nome"].strip()
        if not data["nome"]:
            raise HTTPException(status_code=400, detail="O nome do professor não pode ficar vazio.")

    if "email" in data and data["email"]:
        data["email"] = data["email"].lower()

    if "senha_hash" in data and not data["senha_hash"]:
        data.pop("senha_hash")

    try:
        supabase = get_supabase()

        if "email" in data:
            existing = supabase.table("usuarios").select("id").eq("email", data["email"]).neq("id", usuario_id).limit(1).execute()
            if existing.data:
                raise HTTPException(status_code=409, detail="E-mail já cadastrado para outro usuário.")

        if "sala_id" in data and data["sala_id"] is not None:
            sala = supabase.table("salas").select("id").eq("id", data["sala_id"]).limit(1).execute()
            if not sala.data:
                raise HTTPException(status_code=400, detail="A sala selecionada não existe mais.")

        updated = supabase.table("usuarios").update(data).eq("id", usuario_id).execute()
    except HTTPException:
        raise
    except Exception as exc:
        error_code = getattr(exc, "code", None)
        logger.exception("Falha ao atualizar professor id=%s", usuario_id)
        if error_code == "23505":
            raise HTTPException(status_code=409, detail="E-mail já cadastrado para outro usuário.") from exc
        if error_code == "23503":
            raise HTTPException(status_code=400, detail="A sala selecionada não existe mais.") from exc
        if error_code in {"42703", "PGRST204"}:
            raise HTTPException(status_code=500, detail="O banco do Supabase não reconhece um campo usado na edição. Confira a tabela usuarios e o schema.sql.") from exc
        raise HTTPException(status_code=500, detail="Não foi possível salvar o professor. Consulte os logs do Render.") from exc

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
