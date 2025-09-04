"""
AI Recommendations Prompts Module

This module provides centralized access to all AI recommendations prompts
used throughout the application.
"""

import os
from pathlib import Path

# Get the directory where this file is located
SRC_DIR = Path(__file__).parent
PROMPTS_DIR = SRC_DIR.parent / "prompts"

def _read_prompt_file() -> str:
    """Read the AI recommendations markdown file"""
    prompt_file = PROMPTS_DIR / "ai_recommendations.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"AI recommendations prompt file not found: {prompt_file}")
    
    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()

def _extract_prompt_section(content: str, section_name: str) -> str:
    """Extract a specific prompt section from the markdown content"""
    lines = content.split('\n')
    start_marker = f"## {section_name}"
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if line.strip() == start_marker:
            start_idx = i + 1
        elif start_idx is not None and line.strip() == "## Usage Instructions":
            # For the new format, stop specifically at "Usage Instructions" section
            end_idx = i
            break
    
    if start_idx is None:
        raise ValueError(f"Section '{section_name}' not found in prompt file")
    
    if end_idx is None:
        end_idx = len(lines)
    
    # Extract the content and clean it up
    section_lines = lines[start_idx:end_idx]
    
    # Remove leading/trailing empty lines
    while section_lines and section_lines[0].strip() == "":
        section_lines.pop(0)
    while section_lines and section_lines[-1].strip() == "":
        section_lines.pop()
    
    return '\n'.join(section_lines)

def get_ai_recommendations_prompt(analysis_content: str = "{analysis_content}") -> str:
    """
    Get the unified AI recommendations prompt.
    
    Args:
        analysis_content: The analysis content to include in the prompt
        
    Returns:
        The formatted unified prompt
    """
    content = _read_prompt_file()
    prompt_section = _extract_prompt_section(content, "Unified CV Tailoring Recommendation Generator Prompt")
    
    # For the new prompt structure, we use the entire section content
    # and replace the placeholder with actual analysis content
    return prompt_section.replace("{analysis_content}", analysis_content)

# Legacy functions for backward compatibility
def get_default_prompt(analysis_content: str = "{analysis_content}") -> str:
    """Legacy function - now returns the unified prompt"""
    return get_ai_recommendations_prompt(analysis_content)

def get_detailed_prompt(analysis_content: str = "{analysis_content}") -> str:
    """Legacy function - now returns the unified prompt"""
    return get_ai_recommendations_prompt(analysis_content)

def get_analysis_saver_prompt(analysis_content: str = "{analysis_content}") -> str:
    """Legacy function - now returns the unified prompt"""
    return get_ai_recommendations_prompt(analysis_content)

def get_all_prompts() -> dict:
    """
    Get all available prompts as a dictionary.
    
    Returns:
        Dictionary containing all prompts (now all return the same unified prompt)
    """
    return {
        "unified": get_ai_recommendations_prompt(),
        "default": get_ai_recommendations_prompt(),
        "detailed": get_ai_recommendations_prompt(),
        "analysis_saver": get_ai_recommendations_prompt(),
    }

# Convenience functions for direct access
def get_ai_recommendations_prompt_template() -> str:
    """Get the unified prompt template without content replacement"""
    return get_ai_recommendations_prompt()

def get_default_prompt_template() -> str:
    """Legacy function - now returns the unified prompt template"""
    return get_ai_recommendations_prompt()

def get_detailed_prompt_template() -> str:
    """Legacy function - now returns the unified prompt template"""
    return get_ai_recommendations_prompt()

def get_analysis_saver_prompt_template() -> str:
    """Legacy function - now returns the unified prompt template"""
    return get_ai_recommendations_prompt()
