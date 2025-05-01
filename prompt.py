def generate_low_level_queries(selected_path_data):
    return f"""Based on the following plan:

High-Level Goal: {selected_path_data['hlg_title']}
Estimated Time: {selected_path_data['estimated_time_days']} days
Earning Potential: ${selected_path_data['estimated_earning_usd_per_week']} per week

Now generate 5 low-level goals (LLGs), each:
- Simple and actionable
- Takes < 1 day
- Includes resources
- Beginner friendly
"""