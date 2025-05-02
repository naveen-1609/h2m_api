import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import json
from typing import List, Optional
load_dotenv()

SONAR_API_KEY = os.getenv("SONAR_API_KEY")

class Resource(BaseModel): 
    resource_name: str
    resource_link: str

class LLG(BaseModel):
    llg_title: str
    llg_description: str
    llg_time_to_complete_days: int
    llg_earning_usd_per_week: int
    llg_resources: List[Resource]

class SuccessStory(BaseModel):
    name: str
    story: str
    time_to_first_earning_days: int
    first_earning_usd: int
    citation_link: str

class Path(BaseModel):
    hlg_title: str
    hlg_description: str
    estimated_time_days: int
    estimated_earning_usd_per_week: int
    SuccessStory: SuccessStory

class AnswerFormat(BaseModel):
    hobby: str
    description: str
    paths: List[Path]
    motivational_writeup: str

def search_sonar(query):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
    payload = {
            "model": "sonar",
            "messages": [
                {"role": "system", "content": '''You are helping build a motivational app called Hobby2Money.

The goal is to guide users to earn pocket money ($100–$500/week) from their hobbies in the USA.

Given a user hobby and description, generate:

1. Three High-Level Goals (HLGs) that guide them toward making money.
    - Each HLG must have:
        • Title
        • 1–2 line inspirational description
        • Estimated time to complete (in days)
        • Estimated earnings potential per week (in USD)
2. One real-world success story matching each HLG.
    - Must include:
        • Person or business name
        • Short description of their journey
        • Estimated time they took to start earning
        • Estimated first earnings
        • Link to proof (social media / article / store page, preferably USA-based)
3. A short writeup (2–3 lines) motivating the user to pick this path.
    - It should sound supportive, real, and exciting (not fake hype).

General Rules:
- Prioritize USA examples if possible.
- Use simple English — conversational, motivating tone.
- Stay concise — avoid extra words to optimize tokens.
- Do not assume overnight success — realistic but inspiring timelines.
- Avoid listing billion-dollar companies as success stories.'''
                 },
                {"role": "user", "content": f"How can I earn money through {query}?"}
            ],
            "response_format": {
                "type": "json_schema",
            "json_schema": {
                "schema": AnswerFormat.model_json_schema()
                        }}}   

    response = requests.post(url, headers=headers, json=payload)
    print("🟢 Sonar API Response:", response)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    return json.loads(text) if isinstance(text, str) else text