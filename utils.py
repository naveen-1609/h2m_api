import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
import json
from typing import List

load_dotenv()
SONAR_API_KEY = os.getenv("SONAR_API_KEY")

class Resource(BaseModel):
    resource_name: str
    resource_link: str

class steps(BaseModel):
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
    how_to_do_it: [steps]

class HLGWithLLGs(BaseModel):
    hlg_title: str
    hlg_description: str
    estimated_time_days: int
    estimated_earning_usd_per_week: int
    llgs: List[LLG]  # ✅ LLG list nested under each HLG

class PathWithLLGs(BaseModel):
    path_type: str
    hlgs: List[HLGWithLLGs]  # ✅ Each HLG includes its LLGs

class AnswerFormat_llg(BaseModel):
    hobby: str
    description: str
    path: PathWithLLGs  # ✅ One selected path with LLGs filled in

class HighLevelMilestone(BaseModel):
    hlg_title: str
    hlg_description: str
    estimated_time_days: int
    estimated_earning_usd_per_week: int
    Budget: int

class Path(BaseModel):
    path_type: str
    hlgs: List[HighLevelMilestone]

class SuccessStory(BaseModel):
    name: str
    story: str
    location: str
    description: str
    time_to_first_earning_days: int
    first_earning_usd: int
    citation_link: str

class AnswerFormat(BaseModel):
    hobby: str
    description: str
    paths: List[Path]
    success_story: [SuccessStory]
    motivational_writeup: str


def search_sonar(hobby, description):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": '''
You are a helpful career coach that helps people monetize their hobbies.                
The goal is to guide users to establish some passive income from their hobbies in the USA.
The income could be anywhere between $100 to $500 per week.

Given a hobby input, return 3 distinct paths:

1. Quick Setup Path — minimum investment, quick start, low income (~$100/week).
2. Moderate Setup Path — mid effort, mid income (~$300/week).
3. Long-Term Growth Path — higher effort, larger potential income (~$500+/week).

The Ouick setup path should be the easiest and fastest to start with minimal milestones and increase the complexity as we go along the paths.

Each path must contain:
- 3 to 4 High-Level Goals (HLGs) 
  - Title
  - Description (1–2 lines)
  - Estimated time (in days)
  - Estimated earning potential per week (USD)
  - Budget (USD)

Include:
- 1 real-world success story (preferably from the USA)
- A short motivational write-up (2–3 lines)

DO NOT generate Low-Level Goals (LLGs) yet.

Rules:
- Be realistic, beginner-friendly, and accurate.
- Suggest gear/tools only when necessary.
- Use clear, simple English and direct formatting.'''
            },
            {"role": "user", "content": f"I love {hobby} and {description}. Help me find ways I can earn money doing it."}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": AnswerFormat.model_json_schema()}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    return json.loads(text) if isinstance(text, str) else text

def edit_single_hlg(selected_path, hlg_index: int, user_feedback: str):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
    hlg = selected_path["hlgs"][hlg_index]
    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that edits a High-Level Goal (HLG) inside a selected path based on user feedback while maintaining structure and achievability."
        },
        {
            "role": "user",
            "content": f"""
Original HLG:
Path Type: {selected_path['path_type']}
Title: {hlg['hlg_title']}
Description: {hlg['hlg_description']}
Time: {hlg['estimated_time_days']} days
Income: ${hlg['estimated_earning_usd_per_week']} per week

User Feedback: {user_feedback}

Return only valid JSON. No extra text or explanation.
"""
        }
    ]

    payload = {
        "model": "sonar",
        "messages": messages,
        "web_search_options": {"search_context_size": "low"}
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    raw_text = response.json()["choices"][0]["message"]["content"]

    # 🧹 Clean out code block markers if present
    if raw_text.strip().startswith("```"):
        raw_text = raw_text.strip().strip("```json").strip("```").strip()

    try:
        return json.loads(raw_text)
    except Exception as e:
        print("❌ Failed to parse cleaned JSON:")
        print(raw_text)
        raise e

def generate_low_level_queries_from_path(path_data, hobby_name):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": f"""
You're a Business Coach helping a beginner monetize the hobby '{hobby_name}'.

The user has chosen a path: {path_data['path_type']}.

For each High-Level Goal (HLG) listed below, generate a full, user-friendly roadmap to accomplish it.

HLGs:
{json.dumps(path_data['hlgs'], indent=2)}

Instructions:
- Use Markdown formatting for clarity.
- For each HLG:
  1. Use the HLG title as a section header (e.g., ## HLG: Stock Photography Upload).
  2. Add a section: 🔧 What you need to get started — list equipment/tools with purchase links if needed.
  3. Then write 5 detailed Low-Level Goals (LLGs) under a heading: ✅ LLG Steps
    - Each LLG should be:
      - Simple and actionable (can be done in a day)
      - Include clear steps
      - Mention tools/tutorials if needed
      - Add external links (Amazon, YouTube, etc.)
- The structure must be: HLG → Requirements → LLG Steps (1–5)
- Format must be readable in UI and clean.

Tone: Instructional, supportive, realistic.

IMPORTANT: Do NOT rewrite the HLGs. Just provide the roadmap for the HLGs already listed.
"""
            },
            {"role": "user", "content": f"Help me achieve each milestone step by step providing resources (links, websites, citations) along with guidance ?"}
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": AnswerFormat_llg.model_json_schema()}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    text = response.json()["choices"][0]["message"]["content"]
    return json.loads(text) if isinstance(text, str) else text


# import os
# import requests
# from dotenv import load_dotenv
# from pydantic import BaseModel
# import json
# from typing import List, Optional
# load_dotenv()

# SONAR_API_KEY = os.getenv("SONAR_API_KEY")

# class Resource(BaseModel): 
#     resource_name: str
#     resource_link: str

# class LLG(BaseModel):
#     llg_title: str
#     llg_description: str
#     llg_time_to_complete_days: int
#     llg_earning_usd_per_week: int
#     llg_resources: List[Resource]

# class SuccessStory(BaseModel):
#     name: str
#     story: str
#     time_to_first_earning_days: int
#     first_earning_usd: int
#     citation_link: str

# class Path(BaseModel):
#     hlg_title: str
#     hlg_description: str
#     estimated_time_days: int
#     estimated_earning_usd_per_week: int
#     SuccessStory: SuccessStory

# class AnswerFormat(BaseModel):
#     hobby: str
#     description: str
#     paths: List[Path]
#     motivational_writeup: str

# def search_sonar(query):
#     url = "https://api.perplexity.ai/chat/completions"
#     headers = {"Authorization": f"Bearer {SONAR_API_KEY}"}
#     payload = {
#             "model": "sonar",
#             "messages": [
#                 {"role": "system", "content": '''You are helping build a motivational app called Hobby2Money.

# The goal is to guide users to earn pocket money ($100–$500/week) from their hobbies in the USA.

# Given a user hobby and description, generate:

# 1. Three High-Level Goals (HLGs) that guide them toward making money.
#     - Each HLG must have:
#         • Title
#         • 1–2 line inspirational description
#         • Estimated time to complete (in days)
#         • Estimated earnings potential per week (in USD)
# 2. One real-world success story matching each HLG.
#     - Must include:
#         • Person or business name
#         • Short description of their journey
#         • Estimated time they took to start earning
#         • Estimated first earnings
#         • Link to proof (social media / article / store page, preferably USA-based)
# 3. A short writeup (2–3 lines) motivating the user to pick this path.
#     - It should sound supportive, real, and exciting (not fake hype).

# General Rules:
# - Prioritize USA examples if possible.
# - Use simple English — conversational, motivating tone.
# - Stay concise — avoid extra words to optimize tokens.
# - Do not assume overnight success — realistic but inspiring timelines.
# - Avoid listing billion-dollar companies as success stories.'''
#                  },
#                 {"role": "user", "content": f"How can I earn money through {query}?"}
#             ],
#             "response_format": {
#                 "type": "json_schema",
#             "json_schema": {
#                 "schema": AnswerFormat.model_json_schema()
#                         }}}   

#     response = requests.post(url, headers=headers, json=payload)
#     print("🟢 Sonar API Response:", response)
#     response.raise_for_status()
#     text = response.json()["choices"][0]["message"]["content"]
#     return json.loads(text) if isinstance(text, str) else text