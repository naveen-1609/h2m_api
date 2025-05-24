from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from utils import (
    get_story_summary,
    generate_monetization_paths,
    generate_low_level_queries_from_path,
    edit_single_hlg,
    generate_dummy_stories,
    generate_dummy_paths,
    generate_dummy_llgs,
    generate_dummy_edited_hlg
)

app = FastAPI()


class HobbyRequest(BaseModel):
    hobby: str
    description: Optional[str] = None


class HLGEditRequest(BaseModel):
    selected_path: Dict
    hlg_index: int
    user_feedback: str


class LLGPathRequest(BaseModel):
    hobby: str
    selected_path: Optional[Dict] = None
    updated_path: Optional[Dict] = None


@app.post("/stories/")
async def get_stories(req: HobbyRequest):
    if req.hobby == "xyxy" and req.description == "yzyz":
        return generate_dummy_stories()
    try:
        return get_story_summary(req.hobby, req.description)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate_hlg/")
async def generate_hlg(req: HobbyRequest):
    if req.hobby == "xyxy" and req.description == "yzyz":
        return generate_dummy_paths()
    try:
        return generate_monetization_paths(req.hobby, req.description)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/edit_hlg/")
async def edit_hlg(req: HLGEditRequest):
    if req.hobby == "xyxy" and req.description == "yzyz":
        return {"updated_hlg": generate_dummy_edited_hlg(req.selected_path, req.hlg_index)}
    try:
        updated = edit_single_hlg(req.selected_path, req.hlg_index, req.user_feedback)
        return {"updated_hlg": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate_llgs/")
async def generate_llgs(req: LLGPathRequest):
    if req.hobby == "xyxy":
        return generate_dummy_llgs()
    try:
        final_path = req.updated_path if req.updated_path else req.selected_path
        if not final_path:
            raise ValueError("Either 'selected_path' or 'updated_path' must be provided.")
        return generate_low_level_queries_from_path(final_path, req.hobby)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
