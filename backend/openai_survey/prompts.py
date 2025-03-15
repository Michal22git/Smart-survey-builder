SURVEY_TEMPLATES = {
    "general": """
    Create a survey on the given topic.
    Use a variety of question types (text, single choice, multiple choice, dropdown).
    Each question should be clear and specific.
    """,
    
    "customer_satisfaction": """
    Create a customer satisfaction survey.
    Include questions about:
    - Overall satisfaction with the product/service
    - Customer service experience
    - Value for money
    - Likelihood to recommend to others
    - Areas for improvement
    Use a numerical scale (1-5) for rating questions.
    """,
    
    "market_research": """
    Create a market research survey on the given topic.
    Include questions about:
    - Demographics of respondents
    - Purchasing habits
    - Product/service preferences
    - Factors influencing purchase decisions
    - Awareness of competing brands
    """,
    
    "employee_evaluation": """
    Create an employee evaluation survey.
    Include questions about:
    - Professional skills
    - Teamwork
    - Communication
    - Timeliness
    - Initiative and creativity
    - Areas for development
    """
}

def get_survey_template(template_name: str = "general") -> str:
    """Get a survey template by name."""
    return SURVEY_TEMPLATES.get(template_name, SURVEY_TEMPLATES["general"])

def get_survey_system_prompt(template: str, num_questions: int, language: str) -> str:
    """
    Build a complete system prompt based on template and parameters.
    
    Args:
        template: Template name to use
        num_questions: Suggested number of questions
        language: Survey language
        
    Returns:
        Complete system prompt
    """
    template_content = get_survey_template(template)
    
    system_prompt = f"""
    You are an AI specialized in creating surveys.
    
    {template_content}
    
    Generate exactly {num_questions} questions appropriate for the survey topic.
    For choice-based questions (radio, checkbox, dropdown), include sensible response options (3-7 options).
    The response must be in {language} language.
    
    Return your response as a JSON object with the following structure:
    {{
        "title": "Survey title",
        "description": "Survey description",
        "questions": [
            {{
                "text": "Question text",
                "type": "text|radio|checkbox|dropdown",
                "required": true|false,
                "options": [
                    {{"text": "Option 1"}},
                    {{"text": "Option 2"}}
                ]
            }}
        ]
    }}
    
    Make sure that:
    1. Choice questions (radio, checkbox, dropdown) have options
    2. Text questions don't need options
    3. Each question has all required fields
    """
    
    return system_prompt

def get_question_regeneration_prompt(
    survey_title: str, 
    survey_description: str, 
    other_questions: list,
    question_to_regenerate: dict,
    question_index: int,
    feedback: str
) -> str:
    """
    Build a prompt for regenerating a single question in a survey.
    
    Args:
        survey_title: Title of the survey
        survey_description: Description of the survey
        other_questions: List of other questions in the survey (formatted as strings)
        question_to_regenerate: The question to regenerate
        question_index: Index of the question to regenerate (0-based)
        feedback: User feedback on why to regenerate the question
        
    Returns:
        Complete system prompt for question regeneration
    """
    system_prompt = f"""
    You are regenerating a single question in a survey about "{survey_title}".
    Survey description: {survey_description or 'Not provided'}
    
    The survey contains the following questions:
    {chr(10).join(other_questions)}
    
    You need to regenerate question {question_index + 1}. The current version is:
    "{question_to_regenerate['text']}" (Type: {question_to_regenerate['type']})
    
    User feedback about this question: "{feedback or 'This question needs improvement'}"
    
    Generate a new version of this question that:
    1. Fits well with the rest of the survey
    2. Addresses the user's feedback
    3. Maintains the same question type ({question_to_regenerate['type']})
    4. Includes appropriate options if it's a multiple-choice question
    
    Respond in JSON format with the following structure:
    {{
        "text": "The regenerated question text",
        "type": "{question_to_regenerate['type']}",
        "required": {str(question_to_regenerate['required']).lower()},
        "options": [
            {{"text": "Option 1"}},
            {{"text": "Option 2"}},
            ...
        ]
    }}
    """
    
    return system_prompt

def get_free_text_analysis_prompt() -> str:
    """
    Get the prompt for analyzing free-text survey descriptions.
    
    Returns:
        System prompt for free-text analysis
    """
    return """
    Analyze the following user text and extract parameters needed to generate a survey.
    The user provides a free-form description of the survey they want to create.
    
    Return the result in JSON format with the following fields:
    - prompt: main survey topic (extract the essence of the description)
    - num_questions: suggested number of questions (integer)
    - template: template type (general, customer_satisfaction, market_research, employee_evaluation)
    - language: survey language (language code, e.g., 'en', 'pl')
    
    If the user doesn't specify the number of questions, use 5.
    If the user doesn't specify a template, choose the best fit based on the description.
    If the user doesn't specify a language, use 'en'.
    
    Example response:
    {
        "prompt": "Healthy diet and eating habits",
        "num_questions": 4,
        "template": "general",
        "language": "en"
    }
    """ 