from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_supabase
from backend.dependencies import require_admin
from backend.schemas.equipes import EquipeCreate, EquipeUpdate, EquipeMembroCreate

router = APIRouter(prefix="/equipes", tags=["equipes"])


@router.get("")
def list_equipes(current_user=Depends(require_admin)):
    data = get_supabase().table("equipes").select("*").order("id").execute()
    return data.data or []


@router.get("/sala/{sala_id}")
def list_equipes_por_sala(sala_id: int, current_user=Depends(require_admin)):
    data = get_supabase().table("equipes").select("*").eq("sala_id", sala_id).order("id").execute()
    return data.data or []


@router.get("/{equipe_id}/membros")
def list_membros_equipe(equipe_id: int, current_user=Depends(require_admin)):
    data = get_supabase().table("equipe_membros").select("*, usuarios(nome, id)").eq("equipe_id", equipe_id).execute()
    return data.data or []


@router.post("")
def create_equipe(payload: EquipeCreate, current_user=Depends(require_admin)):
    sala = get_supabase().table("salas").select("id").eq("id", payload.sala_id).limit(1).execute().data or []
    if not sala:
        raise HTTPException(status_code=400, detail="Sala informada não existe.")

    created = get_supabase().table("equipes").insert({
        "nome": payload.nome,
        "sala_id": payload.sala_id,
    }).execute()
    return {"status": "ok", "equipe": created.data[0]}


@router.post("/{equipe_id}/membros")
def add_membro_equipe(equipe_id: int, payload: EquipeMembroCreate, current_user=Depends(require_admin)):
    equipe = get_supabase().table("equipes").select("id, sala_id").eq("id", equipe_id).limit(1).execute().data or []
    if not equipe:
        raise HTTPException(status_code=404, detail="Equipe não encontrada.")

    professor = get_supabase().table("usuarios").select("id, sala_id").eq("id", payload.professor_id).limit(1).execute().data or []
    if not professor:
        raise HTTPException(status_code=404, detail="Professor não encontrado.")

    if professor[0].get("sala_id") != equipe[0].get("sala_id"):
        raise HTTPException(status_code=400, detail="O professor não pertence à sala da equipe.")

    existing = get_supabase().table("equipe_membros").select("id").eq("equipe_id", equipe_id).eq("professor_id", payload.professor_id).execute().data or []
    if existing:
        raise HTTPException(status_code=400, detail="Este professor já está na equipe.")

    created = get_supabase().table("equipe_membros").insert({
        "equipe_id": equipe_id,
        "professor_id": payload.professor_id,
    }).execute()
    return {"status": "ok", "membro": created.data[0]}


@router.delete("/{equipe_id}/membros/{professor_id}")
def remove_membro_equipe(equipe_id: int, professor_id: int, current_user=Depends(require_admin)):
    get_supabase().table("equipe_membros").delete().eq("equipe_id", equipe_id).eq("professor_id", professor_id).execute()
    return {"status": "ok"}


@router.put("/{equipe_id}")
def update_equipe(equipe_id: int, payload: EquipeUpdate, current_user=Depends(require_admin)):
    data = payload.model_dump(exclude_unset=True)
    if "sala_id" in data:
        sala = get_supabase().table("salas").select("id").eq("id", data["sala_id"]).limit(1).execute().data or []
        if not sala:
            raise HTTPException(status_code=400, detail="Sala informada não existe.")

    updated = get_supabase().table("equipes").update(data).eq("id", equipe_id).execute()
    return {"status": "ok", "equipe": updated.data[0] if updated.data else None}


@router.delete("/{equipe_id}")
def delete_equipe(equipe_id: int, current_user=Depends(require_admin)):
    get_supabase().table("equipe_membros").delete().eq("equipe_id", equipe_id).execute()
    get_supabase().table("equipes").delete().eq("id", equipe_id).execute()
    return {"status": "ok"}
