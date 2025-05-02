def generate_low_level_queries(selected_path_data, hobby_name):
    return f"""You're a Business Coach helping a beginner turn their hobby into income. The user has chosen the hobby '{hobby_name}' and selected a High-Level Goal (HLG). Now, generate a detailed roadmap for this HLG.

HLG Title: {selected_path_data['hlg_title']}
HLG Description: {selected_path_data['hlg_description']}
Estimated Time: {selected_path_data['estimated_time_days']} days
Earning Potential: ${selected_path_data['estimated_earning_usd_per_week']} per week

Instructions:
1. Begin with a brief section: "🔧 What you need to get started" — include any gear, apps, subscriptions, or physical items. If recommending a product (like a GoPro, tripod, etc.), provide a direct Amazon or trusted link.
2. Then provide 5 step-by-step Low-Level Goals (LLGs) — these should be:
   - Simple and realistic
   - Actionable in under 1 day
   - Beginner-friendly
   - Include relevant tools, templates, or tutorials with links
3. Clearly format each LLG with: title, short description, how to do it, and supporting resources.

Tone: Friendly, clear, instructional. Be honest — only suggest buying tools if necessary.
"""