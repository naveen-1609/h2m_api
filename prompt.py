def generate_low_level_queries(selected_path_data, hobby_name):
    return f"""
You are an expert monetization coach helping beginners earn through their hobby: "{hobby_name}".

The user selected this High-Level Goal (HLG):
- Title: {selected_path_data['hlg_title']}
- Description: {selected_path_data['hlg_description']}
- Time Estimate: {selected_path_data['estimated_time_days']} days
- Earning Potential: ${selected_path_data['estimated_earning_usd_per_week']} per week

Now generate 2 to 3 Low-Level Goals (LLGs) for this HLG. For each LLG, return:
- llg_title
- llg_description
- llg_time_to_complete_days
- llg_earning_usd_per_week
- llg_resources: List of {{ resource_name, resource_link }}
- motivational_writeup
- why_this_is_important
- how_to_do_it: {{ step_name, step_description, step_resources: [resource] }}
- reference_story
- source_url

Also provide a separate top-level key called "extra_success_stories" with 5–7 short success stories (real, with URLs). Each story must have:
- name
- summary
- location
- income or result
- source_link

All info must be real and verifiable. No made-up stories. Return only valid structured JSON.
"""