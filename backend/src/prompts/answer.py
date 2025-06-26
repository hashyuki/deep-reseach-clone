"""Answer generation prompt templates."""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.

CRITICAL CITATION REQUIREMENTS:
- You MUST include citation markers exactly as they appear in the summaries (e.g. 【0-1】, 【0-2】, 【1-1】, etc.)
- These citation markers will be automatically converted to proper links later
- Place citation markers immediately after the relevant information that comes from that source
- Use multiple citation markers when referencing multiple sources for the same fact
- Every factual claim should be backed by at least one citation marker
- DO NOT create your own citation markers - only use the ones that appear in the summaries below

EXAMPLE:
"Renewable energy capacity increased by 15% in 2023 【0-1】. Solar power specifically grew by 23% 【0-2】, while wind power expanded by 18% 【1-1】."

User Question: {research_topic}

Research Summaries with Citation Markers:
{summaries}

Generate your comprehensive answer below, ensuring every fact is properly cited with the markers from the summaries:"""