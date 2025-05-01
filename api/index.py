from fastapi import FastAPI, HTTPException
from utils import search_sonar
from prompt import generate_low_level_queries

app = FastAPI()
global_hobby_data = {}

@app.post("/generate_path/")
async def generate_path(hobby: str):
    try:
        parsed = search_sonar(hobby)
        global_hobby_data[hobby] = parsed
        return parsed
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/generate_lowlevel/")
async def generate_lowlevel(hobby: str, hlg_index: int = 0):
    try:
        hobby_data = global_hobby_data.get(hobby)
        if not hobby_data:
            raise Exception("High-level data not found. Generate it first.")

        selected_path = hobby_data["paths"][hlg_index]
        query = generate_low_level_queries(selected_path)
        lowlevel_steps = search_sonar(query)
        return {"DetailedPlan": lowlevel_steps}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))