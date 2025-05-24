# index.py — Complete FastAPI app with all 4 endpoints

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from utils import (
    get_story_summary,
    generate_monetization_paths,
    edit_single_hlg,
    generate_low_level_queries_from_path
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
    try:
        return get_story_summary(req.hobby, req.description)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate_hlg/")
async def generate_hlg(req: HobbyRequest):
    try:
        return generate_monetization_paths(req.hobby, req.description)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/edit_hlg/")
async def edit_hlg(req: HLGEditRequest):
    try:
        updated = edit_single_hlg(req.selected_path, req.hlg_index, req.user_feedback)
        return {"updated_hlg": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate_llgs/")
async def generate_llgs(req: LLGPathRequest):
    try:
        final_path = req.updated_path if req.updated_path else req.selected_path
        if not final_path:
            raise ValueError("Either 'selected_path' or 'updated_path' must be provided.")
        return generate_low_level_queries_from_path(final_path, req.hobby)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
