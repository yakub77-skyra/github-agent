"""
Script Writer Module
Uses Groq API to generate engaging video scripts from GitHub repository data
"""

import os
import logging
from typing import Dict, Optional
from groq import Groq

logger = logging.getLogger(__name__)

class ScriptWriter:
    """Generates viral-worthy video scripts using Groq LLM"""
    
    def __init__(self, config: dict):
        self.groq_api_key = config.get('groq_api_key')
        self.llm_client = Groq(api_key=self.groq_api_key)
        self.model = "llama-3.1-70b-versatile"  # Fast and powerful
        
    def generate_script(self, repo: Dict) -> Optional[str]:
        """
        Generate an engaging video script for a GitHub repository
        Optimized for Shorts/Reels (60-90 seconds, ~150-200 words)
        """
        try:
            logger.info(f"Generating script for {repo['name']}...")
            
            # Fetch README content
            readme_content = self._fetch_readme(repo)
            if not readme_content:
                readme_content = repo.get('description', 'No description available')
            
            # Create the prompt optimized for viral content
            prompt = self._create_viral_prompt(repo, readme_content)
            
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a expert tech content creator specializing in viral GitHub repository reviews for YouTube Shorts, Instagram Reels, and Facebook Reels.
                        
Your scripts must:
- Be 60-90 seconds when read aloud (150-200 words max)
- Start with a HOOK that grabs attention in first 3 seconds
- Explain the problem the repo solves in simple terms
- Highlight 2-3 key features with concrete examples
- Include a strong call-to-action at the end
- Use casual, energetic but professional tone
- Avoid jargon, explain technical concepts simply
- Focus on WHY developers should care, not just WHAT it does
- Make it shareable and algorithm-friendly

Format your response as plain text only, no markdown, no sections headers."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300,
                top_p=1.0,
                frequency_penalty=0.3,
                presence_penalty=0.3
            )
            
            script = response.choices[0].message.content.strip()
            
            # Validate script length
            word_count = len(script.split())
            if word_count < 100:
                logger.warning(f"Script too short ({word_count} words), regenerating...")
                return self.regenerate_longer_script(repo, readme_content)
            elif word_count > 250:
                logger.warning(f"Script too long ({word_count} words), truncating...")
                script = ' '.join(script.split()[:200])
            
            logger.info(f"Script generated successfully ({word_count} words)")
            return script
            
        except Exception as e:
            logger.error(f"Error generating script for {repo['name']}: {str(e)}")
            return None
    
    def _create_viral_prompt(self, repo: Dict, readme: str) -> str:
        """Create an optimized prompt for viral script generation"""
        
        return f"""
Create a viral 60-second video script about this GitHub repository:

REPOSITORY: {repo['name']}
DESCRIPTION: {repo['description']}
STARS: {repo['stars']:,} | FORKS: {repo['forks']:,}
LANGUAGE: {repo['language']}
TOPICS: {', '.join(repo['topics'][:5]) if repo['topics'] else 'N/A'}

README CONTENT:
{readme[:3000]}  # Limit to prevent token overflow

KEY POINTS TO COVER:
1. What problem does this solve? (HOOK - first 3 seconds)
2. Why is this better than alternatives?
3. Show 2-3 killer features with examples
4. Who should use this?
5. Call-to-action (star the repo, check it out, etc.)

Make it exciting, clear, and perfect for developers scrolling through their feed!
"""
    
    def regenerate_longer_script(self, repo: Dict, readme: str) -> Optional[str]:
        """Regenerate a longer script if the first attempt was too short"""
        try:
            prompt = f"""
Create a MORE DETAILED 90-second video script about {repo['name']}.

The previous script was too short. Please expand with:
- More specific examples of how to use it
- Real-world use cases
- Comparison with popular alternatives
- Code snippet example (describe it verbally)

README: {readme[:2000]}

Target: 180-200 words, engaging and informative.
"""
            
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a expert tech content creator. Generate detailed but concise scripts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=350
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error regenerating script: {str(e)}")
            return None
    
    def _fetch_readme(self, repo: Dict) -> Optional[str]:
        """Fetch README content for the repository"""
        import requests
        
        readme_urls = [
            f"https://raw.githubusercontent.com/{repo['name']}/main/README.md",
            f"https://raw.githubusercontent.com/{repo['name']}/master/README.md",
            f"https://raw.githubusercontent.com/{repo['name']}/main/readme.md",
            f"https://raw.githubusercontent.com/{repo['name']}/master/readme.md"
        ]
        
        for url in readme_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
            except:
                continue
        
        return None
    
    def optimize_for_platform(self, script: str, platform: str) -> str:
        """Optimize script for specific platform requirements"""
        
        platform_specs = {
            'youtube_shorts': {
                'max_duration': 60,
                'hook_style': 'question_or_shocking_fact',
                'cta': 'Subscribe for more'
            },
            'instagram_reels': {
                'max_duration': 90,
                'hook_style': 'visual_description',
                'cta': 'Follow for daily tech'
            },
            'facebook_reels': {
                'max_duration': 60,
                'hook_style': 'problem_statement',
                'cta': 'Share with developers'
            }
        }
        
        spec = platform_specs.get(platform, platform_specs['youtube_shorts'])
        
        # Add platform-specific elements
        if platform == 'instagram_reels':
            script += "\n\n[Visual: Show code examples with smooth transitions]"
        elif platform == 'youtube_shorts':
            script += "\n\n[End screen: Subscribe button animation]"
        
        return script
