from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils import search_sonar
from prompt import generate_low_level_queries

app = FastAPI()
global_hobby_data = {}

class HobbyRequest(BaseModel):
    hobby: str

class LowLevelRequest(BaseModel):
    hobby: str
    hlg_index: int = 0
    hlg_override: dict = None  # Optional override for updated milestone

@app.post("/generate_path/")
async def generate_path(req: HobbyRequest):
    try:
        parsed = search_sonar(req.hobby)
        global_hobby_data[req.hobby] = parsed
        return parsed
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate_lowlevel/")
async def generate_lowlevel(req: LowLevelRequest):
    try:
        hobby_data = global_hobby_data.get(req.hobby)
        if not hobby_data:
            raise Exception("High-level data not found. Generate it first.")

        selected_path = hobby_data["paths"][req.hlg_index]

        # Allow HLG override before generating LLGs
        if req.hlg_override:
            selected_path.update(req.hlg_override)

        query = generate_low_level_queries(selected_path, req.hobby)
        lowlevel_steps = search_sonar(query)
        return {"DetailedPlan": lowlevel_steps}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))