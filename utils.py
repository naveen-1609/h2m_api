import os
import requests
from dotenv import load_dotenv
import json
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

load_dotenv()
SONAR_API_KEY = os.getenv("SONAR_API_KEY")
SONAR_API_URL = "https://api.perplexity.ai/chat/completions"
HEADERS = {"Authorization": f"Bearer {SONAR_API_KEY}"}


class Resource(BaseModel):
    resource_name: str
    resource_link: str
class story(BaseModel):
    name: str
    summary: str
    location: str
    context: str
    time_to_first_earning_days: int
    first_earning_usd: int
    citation_link: str
class Stories(BaseModel):
    count: int
    story: List[story]
    people_earning: int
    average_income: str
    
class Steps(BaseModel):
    step_name: str
    step_description: str
    step_resources: List[Resource]


class LLG(BaseModel):
    llg_title: str
    llg_description: str
    llg_time_to_complete_days: int
    llg_earning_usd_per_week: int
    llg_resources: List[Resource]
    motivational_writeup: str
    why_this_is_important: str
    how_to_do_it: Steps
    reference_story: Optional[str] = None
    source_url: Optional[str] = None


class HLGWithLLGs(BaseModel):
    hlg_title: str
    hlg_description: str
    estimated_time_days: int
    estimated_earning_usd_per_week: int
    llgs: List[LLG]


class PathWithLLGs(BaseModel):
    path_type: str
    weekly_earning_potential: str
    time_to_first_earning: str
    budget_needed: str
    hlgs: List[HLGWithLLGs]


class AnswerFormat_llg(BaseModel):
    hobby: str
    description: str
    path: PathWithLLGs


class HighLevelMilestone(BaseModel):
    hlg_title: str
    hlg_description: str
    estimated_time_days: int
    estimated_earning_usd_per_week: int
    Budget: int
    estimated_effort: str
    story: story


class Path(BaseModel):
    path_type: str
    weekly_earning_potential: int
    Time_to_first_earning: int
    budget_needed: int
    hlgs: List[HighLevelMilestone]

class SuccessStory(BaseModel):
    name: str
    summary: str
    location: str
    context: str
    time_to_first_earning_days: int
    first_earning_usd: int
    citation_link: str


class AnswerFormat(BaseModel):
    hobby: str
    description: str
    paths: List[Path]
    success_story: List[SuccessStory]
    motivational_writeup: str


def load_dummy_json(filename):
    path = os.path.join(os.path.dirname(__file__), "dummy", filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_dummy_stories():
    return load_dummy_json("dummy_stories.json")

def generate_dummy_paths():
    return load_dummy_json("dummy_paths.json")

def generate_dummy_llgs():
    return load_dummy_json("dummy_llgs.json")

def generate_dummy_edited_hlg(path, index):
    return {
        "hlg_title": "Edited Dummy HLG",
        "hlg_description": "This is your updated dummy HLG.",
        "estimated_time_days": 3,
        "estimated_earning_usd_per_week": 100
    }


def get_story_summary(hobby: str, description: str) -> Dict[str, Any]:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
            "role": "system",
            "content": '''
You are a data analyst and career researcher. Return real statistics and brief, real-world success stories about how people earn money through a specific hobby.
Each story MUST be verifiable with a link.

Return JSON with:
1. "count": number of people who pursue this hobby
2. "story1", "story2", "story3": short stories (1–2 lines) with source links
3. "people_earning": number of people earning through the hobby
4. "average_income": real average weekly/monthly income
'''
        },
        {
            "role": "user",
            "content": f"My hobby is {hobby}. I do it {description}. Provide real earnings stories and stats."
        }
    ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": Stories.model_json_schema()}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    return json.loads(text) if isinstance(text, str) else text


def generate_monetization_paths(hobby: str, description: str) -> Dict[str, Any]:
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
    payload = {
        "model": "sonar-pro",
        "messages": [
            {
                "role": "system",
                "content": '''
    You're a monetization strategist. Create 3 earning paths (Quick, Mid, Ambitious) based on a user’s hobby.

    Each path must include:
    - path_type
    - weekly_earning_potential
    - time_to_first_earning
    - budget_needed
    - hlgs: 4 steps with:
    - hlg_title
    - hlg_description
    - estimated_time_days
    - estimated_earning_usd_per_week
    - story, story_url

    Also add: extra_success_stories (5–7):
    - name
    - summary
    - location
    - income or impact
    - source_link

    Only return structured JSON. No fake info.
    '''
        },
        {
            "role": "user",
            "content": f"My hobby is {hobby}. I do it {description}. Give 3 monetization paths and 5–7 real stories."
        }
    ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": AnswerFormat.model_json_schema()}
        }
    }

    response = requests.post(SONAR_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    return json.loads(text) if isinstance(text, str) else text


def edit_single_hlg(selected_path, hlg_index: int, user_feedback: str):
    hlg = selected_path["hlgs"][hlg_index]
    payload = {
        "model": "sonar",
        "messages": [
        {
            "role": "system",
            "content": "Edit this one HLG in-place based on feedback. Keep others unchanged."
        },
        {
            "role": "user",
            "content": f"""
HLG:
Path Type: {selected_path['path_type']}
Title: {hlg['hlg_title']}
Description: {hlg['hlg_description']}
Time: {hlg['estimated_time_days']} days
Income: ${hlg['estimated_earning_usd_per_week']} per week

User Feedback: {user_feedback}
Only return valid JSON for the updated HLG.
"""
        }
    ]    
    }

    response = requests.post(SONAR_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    raw_text = response.json()["choices"][0]["message"]["content"]

    if raw_text.strip().startswith("```"):
        raw_text = raw_text.strip().strip("```json").strip("```").strip()

    return json.loads(raw_text)


def generate_low_level_queries_from_path(path_data, hobby_name):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
    payload = {
        "model": "sonar-pro",
        "messages": [
        {
            "role": "system",
            "content": f"""
You are a Business Coach helping monetize the hobby '{hobby_name}'.

For each HLG below, generate:
- 2–3 Low-Level Goals (LLGs), each with:
  - llg_title
  - llg_description
  - llg_time_to_complete_days
  - llg_earning_usd_per_week
  - llg_resources: list of {{ resource_name, resource_link }}
  - motivational_writeup
  - why_this_is_important
  - how_to_do_it: {{ step_name, step_description, step_resources }}
  - reference_story
  - source_url

ALSO return a top-level key:
extra_success_stories: list of 5–7 stories with:
- name, summary, location, income, source_link

HLGs:
{json.dumps(path_data['hlgs'], indent=2)}

Return only valid JSON. No extra commentary.
            """
        },
        {
            "role": "user",
            "content": "Give step-by-step plans and real success stories with sources."
        }
    ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": AnswerFormat_llg.model_json_schema()}
        }
    }
        
    # Debug helper
    print("📤 Sending payload to Sonar:")
    print(json.dumps(payload, indent=2))

    # Make request
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    # Handle response
    result = response.json()["choices"][0]["message"]["content"]
    return json.loads(result) if isinstance(result, str) else result