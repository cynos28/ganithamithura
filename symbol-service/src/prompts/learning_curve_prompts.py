"""
Prompts for the Learning Curve Agent.
Focuses on Adaptive Teaching Styles.
"""

import json

def get_teaching_style_prompt(grade, topic, style):
    """
    Generate a lesson script based on a specific PEDAGOGICAL STYLE.
    """
    # Parse detailed curriculum if available
    curriculum_dict = {}
    if isinstance(topic, str):
        try:
             curriculum_dict = json.loads(topic)
             # print(f"DEBUG PROMPT: Successfully loaded JSON. Keys: {list(curriculum_dict.keys())}")
        except Exception as e:
             print(f"DEBUG PROMPT: JSON LOAD FAILED: {e}")
             print(f"DEBUG PROMPT TOPIC WAS: {topic}")
             pass
    elif isinstance(topic, dict):
        curriculum_dict = topic

    # Extract Pedagogical Data from new spec
    focus = curriculum_dict.get('focus', 'Math topic')
    intro_narrative = curriculum_dict.get('narrative_intro', f'Hello! Today we learn about {focus}.')
    story_1_guide = curriculum_dict.get('story_1_guide', f'Tell a simple story about {focus}.')
    story_2_guide = curriculum_dict.get('story_2_guide', 'Tell another example.')
    conclusion_guide = curriculum_dict.get('conclusion_guide', 'Encourage the student.')
    
    what_taught = curriculum_dict.get('what_is_taught', '')
    should_understand = ", ".join(curriculum_dict.get('students_should_understand', []))
    
    # Extract Numerical Constraints
    addends_max = curriculum_dict.get('addends_max', curriculum_dict.get('operand_max', 10))
    result_max = curriculum_dict.get('result_max', 20)
    allowed_ops = ", ".join(curriculum_dict.get('operations', ['+']))

    base = f"""
    You are an expert Math Tutor Agent.
    Goal: SPEAK the provided script to the student.
    
    === CURRICULUM CONTEXT ===
    TOPIC: {focus}
    MAIN CONCEPT: {what_taught}
    
    === STRICT MATH CONSTRAINTS ===
    - Max Number: {addends_max}
    - Max Result: {result_max}
    
    === INSTRUCTIONS ===
    - You will be provided with specific text for the Welcome, Stories, and Conclusion.
    - Use the provided text as a GUIDE.
    - Vary the phrasing slightly each time so it sounds fresh.
    - Keep vocabulary VERY SIMPLE (Grade 1 level). NO complex words.
    - DO NOT CHANGE THE NUMBERS.
    - Paraphrase slightly but keep the core meaning and numbers.
    - DO NOT ADD "Here is a story...". JUST TELL THE STORY.
    - OTHERWISE, READ THE SCRIPT VERBATIM.
    
    === YOUR SCRIPT STRUCTURE (FOLLOW EXACTLY) ===
    
    {intro_narrative}
    
    {story_1_guide}
    
    {story_2_guide}
    
    {conclusion_guide}
    
    **CRITICAL RULES**:
    - DO NOT USE HEADERS like "Voice:" or "Narrator:".
    - OUTPUT ONLY THE SPOKEN TEXT under the STEP headers.
    - KEEP NUMBERS <= {addends_max}. IF YOU USE LARGER NUMBERS, YOU FAIL.
    """
    
    return base
