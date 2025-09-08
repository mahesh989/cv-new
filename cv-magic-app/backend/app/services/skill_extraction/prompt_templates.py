"""
Prompt Templates for Skill Extraction

Contains all the prompt templates used for AI-based skill extraction
"""

class SkillExtractionPrompts:
    """Centralized prompt templates for skill extraction"""
    
    @staticmethod
    def get_skill_extraction_template(document_type: str, document_text: str) -> str:
        """
        Create standardized prompt for both CV and JD extraction
        
        Args:
            document_type: Type of document ("CV" or "Job Description")
            document_text: The actual text content to analyze
            
        Returns:
            Formatted prompt string
        """
        return f'''
Extract SOFT SKILLS, TECHNICAL SKILLS, and DOMAIN KEYWORDS from this {document_type.lower()} and categorize them:

IMPORTANT: Only extract skills/keywords that are explicitly mentioned or have very strong textual evidence. Avoid assumptions or industry-standard inferences. Do not repeat skills/keywords that are already mentioned.

## {document_type.upper()}:
{document_text}

## SOFT SKILLS:
EXPLICIT (directly stated): List soft skills clearly mentioned
STRONGLY IMPLIED (very likely based on responsibilities): List soft skills heavily suggested with strong textual evidence

## TECHNICAL SKILLS:
EXPLICIT (directly stated): List technical skills, tools, software, qualifications clearly mentioned
STRONGLY IMPLIED (very likely based on responsibilities): List technical skills heavily suggested with strong textual evidence

## DOMAIN KEYWORDS:
EXPLICIT:  Your task is to extract **domain-specific keywords** related strictly to the **job role or functional expertise**, NOT the industry, organization, or its values.
  List **industry terms**, **role-specific language**, **tools**, **methodologies**, **compliance concepts**, and **domain knowledge** that are **directly mentioned** in the {document_type.lower()}.

STRONGLY IMPLIED:
  Your task is to extract **domain-specific keywords** related strictly to the **job role or functional expertise**, NOT the industry, organization, or its values.
  List **domain-relevant concepts** that are **heavily suggested** by the context, responsibilities, or required outputs — even if not explicitly named.

### DO NOT include:
- Company or organization names
- Program/service titles
- Sector-level social causes
- Values or mission statements

## CONTEXT EVIDENCE:
For each skill/keyword, provide the relevant quote from the {document_type.lower()} that supports the extraction

**CRITICAL OUTPUT REQUIREMENT:**
You MUST end your response with EXACTLY these three Python lists (no extra text after them):

SOFT_SKILLS = ["skill1", "skill2", "skill3"]
TECHNICAL_SKILLS = ["skill1", "skill2", "skill3"]  
DOMAIN_KEYWORDS = ["keyword1", "keyword2", "keyword3"]

**EXAMPLE OUTPUT FORMAT:**
SOFT_SKILLS = ["Communication", "Leadership", "Problem-solving"]
TECHNICAL_SKILLS = ["Python", "SQL", "Tableau"]
DOMAIN_KEYWORDS = ["Data analysis", "Business intelligence", "Machine learning"]

Text: """
{document_text.strip()}
"""
'''

    @staticmethod
    def get_system_prompt(document_type: str) -> str:
        """
        Get system prompt for the AI model
        
        Args:
            document_type: Type of document being analyzed
            
        Returns:
            System prompt string
        """
        return f"You are a precise extractor of skills from professional {document_type.lower()}s. Analyze the text and provide detailed skill extraction with supporting evidence, then end with clean Python lists."
