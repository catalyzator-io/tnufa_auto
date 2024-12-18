from src.utils.models import EnhancedContentSection
from src.utils.taxonomy import taxonomy, section_info

_prompt_template = """
You are a Domain expert specializing in startup due diligence, with proficiency in analyzing startup pitches and structuring comprehensive, detailed reports. Your task is to evaluate the provided startup pitch and supplementary materials to produce a thorough due diligence report. The report should be organized into clearly labeled sections, following the framework outlined below. For each section, analyze the information provided, identify gaps, and suggest actionable improvements or clarifications where needed. Use bullet points for clarity and provide concise yet detailed explanations.

**Key Instructions:**
1. Address every section of the report, even if the pitch lacks sufficient information for certain aspects. Explicitly note missing details, propose relevant questions to fill gaps, and suggest enhancements to strengthen the pitch.
2. Tailor your analysis to reflect domain-specific terminology and concepts, ensuring relevance for investors, advisors, or stakeholders conducting due diligence.
3. Use the embedded taxonomy (below) to ensure all critical aspects of startup due diligence are covered comprehensively. Identify and address any missing information or underdeveloped points using these categories as a guide.
4. Maintain a professional tone suitable for decision-makers, ensuring clarity, precision, and a logical structure.
5. Use a down to earth tone, and write in a way that is easy to understand.
6. **In each section write a detailed analysis. the structure is a summary, bullet points, and a 3 paragraph detailed analysis. It is important to have a detailed analysis of each section!**

**Report Framework** (sections):

{section_info}

**Taxonomy**:

Use the following categories to enrich your analysis in each section:

{taxonomy}

**Actionable Gap Analysis**:  
For every missing or incomplete section, explicitly note the gap and suggest detailed, practical improvements or follow-up questions.

**Input**: {files_content}
**Output**: A structured due diligence report covering all aspects above, with detailed and actionable insights.

**Format**:
- Start each section with a summary.  
- Follow with subpoints or bullet points detailing the analysis.  
- have a 3 paragraph detailed analysis of the section.
- Clearly separate actionable suggestions or notes for missing details.
- Use `h2` markdown headers for section titles.
- Use the exact titles "Summary", "Notes", "Detailed Analysis", "Actionable Gap Analysis" in this exact order for the parts of each section.
- Each part's title should be in an `h3` markdown header.

Deliver a polished, investor-ready report that captures all essential dimensions of due diligence.
"""

def get_prompt(files_content: str) -> str:
    taxonomy_str = "\n".join([
        f"- **{category}**: {', '.join(keywords)}"
        for category, keywords in taxonomy.items()
    ])
    section_info_str = "\n".join([
        f"{i+1}. **{title}**: {description}"
        for i, (title, description) in enumerate(section_info.items())
    ])
    return _prompt_template.format(
        taxonomy=taxonomy_str,
        files_content=files_content,
        section_info=section_info_str
    )


def extract_sections(content: str) -> list[EnhancedContentSection]:
    """Extract the sections from the content"""
    # Split content into sections based on h2 headers
    sections = [s.strip() for s in content.split('## ') if s.strip()]
    
    def _parse_section_title(section: str) -> str:
        return section.split('\n', maxsplit=1)[0].strip()
    
    def _parse_part_title(part: str) -> str:
        return part.split('\n', maxsplit=1)[0].replace(' ', '_').lower().strip()
        
    # Process each section into a dictionary
    parsed_sections = {
        # Section title is first line
        _parse_section_title(section): {
            # Part title is second line
            _parse_part_title(part): part.split('\n', maxsplit=1)[1].strip()
            # Split by h3 headers and skip first empty element
            for part in section.split('### ')[1:]
        }
        for section in sections
    }
    
    return [EnhancedContentSection(title=title, **section) for title, section in parsed_sections.values()]
