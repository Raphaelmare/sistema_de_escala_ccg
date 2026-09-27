from fastapi import APIRouter, Depends, HTTPException

from backend.database import get_supabase
from backend.dependencies import require_admin
from backend.schemas.duplas import DuplaCreate, DuplaUpdate

router = APIRouter(prefix="/duplas", tags=["duplas"])


@router.get("")
def list_duplas(current_user=Depends(require_admin)):
    data = get_supabase().table("duplas").select("*").order("id").execute()
    return data.data or []


@router.get("/sala/{sala_id}")
def list_duplas_por_sala(sala_id: int, current_user=Depends(require_admin)):
    data = get_supabase().table("duplas").select("*").eq("sala_id", sala_id).order("id").execute()
    return data.data or []


@router.post("")
def create_dupla(payload: DuplaCreate, current_user=Depends(require_admin)):
    if payload.professor_1_id == payload.professor_2_id:
        raise HTTPException(status_code=400, detail="O mesmo professor não pode estar em ambos os campos.")

    sala = get_supabase().table("salas").select("id").eq("id", payload.sala_id).limit(1).execute().data or []
    if not sala:
        raise HTTPException(status_code=400, detail="Sala informada não existe.")

    professores = get_supabase().table("usuarios").select("id, sala_id").in_("id", [payload.professor_1_id, payload.professor_2_id]).execute().data or []
    professor_map = {int(item["id"]): item for item in professores}

    if payload.professor_1_id not in professor_map or professor_map[payload.professor_1_id].get("sala_id") != payload.sala_id:
        raise HTTPException(status_code=400, detail="O professor 1 não pertence à sala selecionada.")

    if payload.professor_2_id is not None:
        if payload.professor_2_id not in professor_map or professor_map[payload.professor_2_id].get("sala_id") != payload.sala_id:
            raise HTTPException(status_code=400, detail="O professor 2 não pertence à sala selecionada.")

    created = get_supabase().table("duplas").insert({
        "nome_dupla": payload.nome_dupla,
        "sala_id": payload.sala_id,
        "professor_1_id": payload.professor_1_id,
        "professor_2_id": payload.professor_2_id,
    }).execute()
    return {"status": "ok", "dupla": created.data[0]}


@router.put("/{dupla_id}")
def update_dupla(dupla_id: int, payload: DuplaUpdate, current_user=Depends(require_admin)):
    data = payload.model_dump(exclude_unset=True)
    updated = get_supabase().table("duplas").update(data).eq("id", dupla_id).execute()
    return {"status": "ok", "dupla": updated.data[0] if updated.data else None}


@router.delete("/{dupla_id}")
def delete_dupla(dupla_id: int, current_user=Depends(require_admin)):
    get_supabase().table("duplas").delete().eq("id", dupla_id).execute()
    return {"status": "ok"}
