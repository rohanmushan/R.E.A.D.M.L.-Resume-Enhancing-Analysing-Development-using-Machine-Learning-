import google.generativeai as genai
from typing import Dict, List, Tuple
import streamlit as st
import time
import json

def initialize_gemini(api_key: str):
    """Initialize Gemini API with the provided key"""
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Use gemini-1.5-flash model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test the model
        response = model.generate_content("Test")
        if response:
            return model
        
    except Exception as e:
        if "429" in str(e):  # Rate limit error
            st.error("Rate limit exceeded. Please wait a few minutes before trying again.")
            st.info("""z
            To avoid rate limits:
            1. Wait a few minutes between requests
            2. Keep your prompts concise
            3. Consider upgrading to a paid API tier
            """)
        else:
            st.error(f"Failed to initialize Gemini API: {str(e)}")
            st.info("""
            Please check:
            1. Your API key is valid
            2. You have internet connection
            3. The API service is available in your region
            """)
        return None

def analyze_resume_content(model, resume_data: Dict) -> Dict:
    """Analyze resume content using Gemini API with rate limit handling"""
    if not model:
        return {
            'profile_analysis': "AI analysis unavailable. Please check API configuration.",
            'skills_analysis': "AI analysis unavailable. Please check API configuration."
        }
    
    try:
        # Add delay between requests to avoid rate limits
        time.sleep(2)
        
        # Enhanced profile analysis prompt with more detailed instructions
        profile_prompt = f"""
        As an expert resume reviewer and hiring manager with extensive experience in {resume_data['profile_summary']['target_role']} roles, 
        perform a comprehensive analysis of this professional profile:

        TARGET ROLE: {resume_data['profile_summary']['target_role']}
        CURRENT SUMMARY: {resume_data['profile_summary']['summary']}
        SKILLS: {', '.join(resume_data['skills']['programming'] + resume_data['skills'].get('frameworks', []))}
        
        Provide detailed, actionable feedback in the following categories:

        1. Profile Strengths (25%):
        • Identify strong points that align with the target role
        • Highlight effective achievements and metrics
        • Note well-presented technical capabilities
        • Recognize unique selling points
        • Evaluate industry-specific expertise

        2. Areas for Improvement (25%):
        • Point out specific content gaps
        • Identify missing key qualifications
        • Suggest concrete additions
        • Note unclear or weak descriptions
        • Recommend better ways to present experience

        3. Industry Alignment (20%):
        • Compare with current industry standards
        • List missing critical keywords
        • Suggest relevant certifications
        • Recommend emerging technical skills
        • Note competitive differentiators

        4. Content Enhancement (15%):
        • Provide specific metrics to add
        • Suggest impactful action verbs
        • Recommend achievement formats
        • List quantifiable examples
        • Propose better ways to describe projects

        5. Optimization Tips (15%):
        • Suggest structural improvements
        • Recommend format changes
        • Propose keyword placements
        • Advise on content organization
        • Note best practices for the role

        Format your response with clear bullet points and complete sentences.
        Focus on actionable, specific advice that will improve the resume's effectiveness.
        Prioritize recommendations based on their potential impact.
        """
        
        profile_response = model.generate_content(profile_prompt)
        
        # Add delay between requests
        time.sleep(2)
        
        # Enhanced skills analysis prompt
        skills_prompt = f"""
        As a senior technical recruiter specializing in {resume_data['profile_summary']['target_role']} positions,
        analyze these technical competencies:

        ROLE: {resume_data['profile_summary']['target_role']}
        TECHNICAL SKILLS: {', '.join(resume_data['skills']['programming'])}
        FRAMEWORKS: {', '.join(resume_data['skills'].get('frameworks', []))}
        OTHER SKILLS: {', '.join(resume_data['skills'].get('other', []))}
        
        Provide a detailed analysis in these areas:

        1. Technical Skill Assessment (30%):
        • Evaluate current technical stack
        • Rate skill relevance for the role
        • Identify critical missing skills
        • Suggest priority additions
        • Compare with industry standards

        2. Framework & Tool Analysis (25%):
        • Assess framework proficiency needs
        • Recommend complementary tools
        • Suggest version-specific skills
        • Note emerging technologies
        • Identify obsolete technologies

        3. Industry Requirements (20%):
        • List must-have skills for 2024
        • Identify emerging technologies
        • Suggest certification paths
        • Note competitive advantages
        • Compare with market demands

        4. Skill Development Plan (15%):
        • Prioritize learning objectives
        • Recommend learning resources
        • Suggest timeline for upskilling
        • List quick wins
        • Propose long-term goals

        5. Market Positioning (10%):
        • Analyze unique skill combinations
        • Suggest specialization paths
        • Identify high-demand niches
        • Note salary-boosting skills
        • Recommend portfolio projects

        Format your response with clear bullet points and complete sentences.
        Focus on concrete, actionable recommendations.
        Consider both immediate needs and future career growth.
        """
        
        skills_response = model.generate_content(skills_prompt)
        
        return {
            'profile_analysis': profile_response.text if profile_response else "Analysis failed",
            'skills_analysis': skills_response.text if skills_response else "Analysis failed"
        }
    except Exception as e:
        if "429" in str(e):  # Rate limit error
            st.error("Rate limit exceeded. Please wait a few minutes before trying again.")
            return {
                'profile_analysis': "Analysis paused: Rate limit exceeded. Please try again in a few minutes.",
                'skills_analysis': "Analysis paused: Rate limit exceeded. Please try again in a few minutes."
            }
        st.error(f"Error during resume analysis: {str(e)}")
        return {
            'profile_analysis': f"Analysis failed: {str(e)}",
            'skills_analysis': f"Analysis failed: {str(e)}"
        }

def get_ats_optimization(model, resume_data: Dict) -> Dict:
    """Get ATS optimization suggestions using Gemini API"""
    if not model:
        return {'ats_analysis': "ATS analysis unavailable. Please check API configuration."}
    
    try:
        # Add delay before request
        time.sleep(2)
        
        # Enhanced ATS analysis prompt with comprehensive scoring criteria
        prompt = f"""
        As an expert ATS (Applicant Tracking System) analyst, perform a detailed evaluation of this resume for the role of {resume_data['profile_summary']['target_role']}.

        Resume Content:
        - Target Role: {resume_data['profile_summary']['target_role']}
        - Professional Summary: {resume_data['profile_summary']['summary']}
        - Technical Skills: {', '.join(resume_data['skills']['programming'])}
        - Frameworks/Libraries: {', '.join(resume_data['skills'].get('frameworks', []))}
        - Other Skills: {', '.join(resume_data['skills'].get('other', []))}
        - Projects: {json.dumps([p['title'] for p in resume_data['projects']])}
        - Education: {resume_data['education']['degree']} from {resume_data['education']['university']}

        Provide a comprehensive ATS analysis with the following structure:

        1. ATS Compatibility Score (30%):
        • Overall Score: [0-100]
        • Keyword Relevance: [0-30]
        • Format Compliance: [0-25]
        • Skills Match: [0-25]
        • Education Match: [0-20]
        • Detailed score breakdown
        • Industry benchmark comparison

        2. Keyword Optimization (25%):
        • Critical keywords found
        • Missing essential keywords
        • Keyword placement analysis
        • Frequency optimization
        • Context relevance
        • Industry-specific terms

        3. Format & Structure (20%):
        • Section organization
        • Content hierarchy
        • Heading consistency
        • Bullet point usage
        • White space utilization
        • File format compliance

        4. Content Enhancement (15%):
        • Action verb usage
        • Metrics and achievements
        • Technical terminology
        • Role-specific language
        • Experience description
        • Project highlights

        5. ATS-Specific Recommendations (10%):
        • File format guidelines
        • Parsing optimization
        • Layout improvements
        • Font considerations
        • Special character usage
        • Mobile compatibility

        Format your response with clear sections and bullet points.
        Provide specific, actionable recommendations.
        Include both quick fixes and strategic improvements.
        Consider multiple ATS platforms' requirements.
        """
        
        response = model.generate_content(prompt)
        return {
            'ats_analysis': response.text if response else "ATS analysis failed"
        }
    except Exception as e:
        if "429" in str(e):  # Rate limit error
            st.error("Rate limit exceeded. Please wait a few minutes before trying again.")
            return {
                'ats_analysis': "Analysis paused: Rate limit exceeded. Please try again in a few minutes."
            }
        st.error(f"Error during ATS analysis: {str(e)}")
        return {
            'ats_analysis': f"Analysis failed: {str(e)}"
        }

def generate_achievements_suggestions(model, resume_data: Dict) -> List[str]:
    """Generate achievement suggestions based on experience"""
    
    prompt = f"""
    Based on this professional profile:
    Role: {resume_data['profile_summary']['target_role']}
    Skills: {', '.join(resume_data['skills']['programming'] + resume_data['skills']['frameworks'])}
    Projects: {', '.join(p['title'] for p in resume_data['projects'])}
    
    Suggest 5 quantifiable achievements that would strengthen this resume.
    Format each achievement with:
    1. Action verb
    2. Specific metric
    3. Impact statement
    """
    
    response = model.generate_content(prompt)

def extract_improved_content(analysis_text: str) -> Dict[str, str]:
    """Extract improved content from AI analysis"""
    try:
        # Split analysis into sections
        sections = analysis_text.split('\n')
        improved_content = {}
        
        current_section = None
        current_content = []
        
        for line in sections:
            line = line.strip()
            if not line:
                continue
                
            # Check for section headers
            if line.startswith('1.') and ('Enhanced Version' in line or 'Version' in line):
                if current_section and current_content:
                    improved_content[current_section] = '\n'.join(current_content)
                current_section = 'enhanced_version'
                current_content = []
            elif line.startswith('2.') and 'Key Improvements' in line:
                if current_section and current_content:
                    improved_content[current_section] = '\n'.join(current_content)
                current_section = 'improvements'
                current_content = []
            elif line.startswith('3.') and 'Missing Keywords' in line:
                if current_section and current_content:
                    improved_content[current_section] = '\n'.join(current_content)
                current_section = 'keywords'
                current_content = []
            elif line.startswith('4.') and 'Metrics' in line:
                if current_section and current_content:
                    improved_content[current_section] = '\n'.join(current_content)
                current_section = 'metrics'
                current_content = []
            elif current_section:
                if not line.startswith(('1.', '2.', '3.', '4.')):
                    current_content.append(line)
        
        # Add the last section
        if current_section and current_content:
            improved_content[current_section] = '\n'.join(current_content)
            
        return improved_content
    except Exception as e:
        st.error(f"Error extracting improvements: {str(e)}")
        return {}

def apply_ai_suggestions(resume_data: Dict, analysis_data: Dict) -> Tuple[Dict, List[str]]:
    """Apply AI suggestions to resume data"""
    try:
        updated_data = resume_data.copy()
        changes_made = []
        
        # Extract improvements from profile analysis
        if 'profile_analysis' in analysis_data:
            profile_improvements = extract_improved_content(analysis_data['profile_analysis'])
            
            # Apply enhanced version of summary if available
            if 'enhanced_version' in profile_improvements:
                old_summary = updated_data['profile_summary']['summary']
                new_summary = profile_improvements['enhanced_version']
                if new_summary and new_summary != old_summary:
                    updated_data['profile_summary']['summary'] = new_summary
                    changes_made.append("Updated profile summary with AI suggestions")
            
            # Add suggested keywords to skills
            if 'keywords' in profile_improvements:
                keywords = [k.strip() for k in profile_improvements['keywords'].split(',') 
                          if k.strip() and k.strip() not in updated_data['skills'].get('other', [])]
                if keywords:
                    if 'other' not in updated_data['skills']:
                        updated_data['skills']['other'] = []
                    updated_data['skills']['other'].extend(keywords)
                    changes_made.append(f"Added {len(keywords)} suggested keywords to skills")
        
        # Apply skills improvements
        if 'skills_analysis' in analysis_data:
            skills_improvements = extract_improved_content(analysis_data['skills_analysis'])
            
            # Add missing critical skills
            if 'Critical Missing Skills' in skills_improvements:
                new_skills = [s.strip() for s in skills_improvements['Critical Missing Skills'].split(',')
                            if s.strip() and s.strip() not in updated_data['skills'].get('programming', [])]
                if new_skills:
                    if 'programming' not in updated_data['skills']:
                        updated_data['skills']['programming'] = []
                    updated_data['skills']['programming'].extend(new_skills)
                    changes_made.append(f"Added {len(new_skills)} suggested technical skills")
        
        # Apply ATS optimization suggestions
        if 'ats_analysis' in analysis_data:
            ats_improvements = extract_improved_content(analysis_data['ats_analysis'])
            
            # Add format improvements to the changes list
            if 'Format Improvements' in ats_improvements:
                changes_made.append("ATS Format Suggestions:")
                for line in ats_improvements['Format Improvements'].split('\n'):
                    if line.strip():
                        changes_made.append(f"- {line.strip()}")
        
        if not changes_made:
            changes_made.append("No changes were necessary - your resume already follows the suggestions!")
            
        return updated_data, changes_made
        
    except Exception as e:
        st.error(f"Error applying suggestions: {str(e)}")
        return resume_data, [f"Failed to apply suggestions: {str(e)}"]
 