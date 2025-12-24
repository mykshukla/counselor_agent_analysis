DEVELOPER_PROMPT="""
Extract INTENT strictly from the user request.

Allowed intents:
- campaign_performance
- counselor_performance
- campaign_counselor_breakdown
- interaction_analysis
- future_campaign_recommendation

Return ONLY valid JSON:
{
  "intent": "<one_of_the_above>"
}



"""