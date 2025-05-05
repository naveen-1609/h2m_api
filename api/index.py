from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from utils import search_sonar, generate_low_level_queries_from_path, edit_single_hlg

app = FastAPI()

class HobbyRequest(BaseModel):
    hobby: str

class HLGEditRequest(BaseModel):
    selected_path: dict
    hlg_index: int
    user_feedback: str

class LLGPathRequest(BaseModel):
    hobby: str
    selected_path: Optional[dict] = None
    updated_path: Optional[dict] = None

@app.post("/generate_path/")
async def generate_path(req: HobbyRequest):
    try:
        parsed = search_sonar(req.hobby)
        return parsed
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/edit_hlg/")
async def edit_hlg(req: HLGEditRequest):
    try:
        updated = edit_single_hlg(req.selected_path, req.hlg_index, req.user_feedback)
        return {"updated_hlg": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate_lowlevel_path/")
async def generate_lowlevel_path(req: LLGPathRequest):
    try:
        final_path = req.updated_path if req.updated_path else req.selected_path
        if not final_path:
            raise ValueError("Either 'selected_path' or 'updated_path' must be provided.")

        # query = generate_low_level_queries_from_path(final_path, req.hobby)
        plan = generate_low_level_queries_from_path(final_path, req.hobby)
        return {"DetailedPlan": plan}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from utils import search_sonar, generate_low_level_queries_from_path, edit_single_hlg

# app = FastAPI()

# class HobbyRequest(BaseModel):
#     hobby: str

# class HLGEditRequest(BaseModel):
#     selected_path: dict
#     hlg_index: int
#     user_feedback: str

# class LLGPathRequest(BaseModel):
#     hobby: str
#     selected_path: dict

# @app.post("/generate_path/")
# async def generate_path(req: HobbyRequest):
#     try:
#         parsed = search_sonar(req.hobby)
#         return parsed
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @app.post("/edit_hlg/")
# async def edit_hlg(req: HLGEditRequest):
#     try:
#         updated_hlg = edit_single_hlg(req.selected_path, req.hlg_index, req.user_feedback)
#         # Replace the specific HLG with the edited one
#         req.selected_path["hlgs"][req.hlg_index] = updated_hlg
#         return {"updated_path": req.selected_path}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @app.post("/generate_lowlevel_path/")
# async def generate_lowlevel_path(req: LLGPathRequest):
#     try:
#         query = generate_low_level_queries_from_path(req.selected_path, req.hobby)
#         plan = search_sonar(query)
#         return {"DetailedPlan": plan}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
