"""
Self-Healer Module
AI-powered error detection, analysis, and automatic fix generation
"""

import os
import logging
import re
from typing import Dict, Optional, List
from groq import Groq

logger = logging.getLogger(__name__)

class SelfHealer:
    """Autonomous error detection and fixing system"""
    
    def __init__(self, config: dict):
        self.groq_api_key = config.get('groq_api_key')
        self.llm_client = Groq(api_key=self.groq_api_key)
        self.model = "llama-3.1-70b-versatile"
        self.max_retries = config.get('max_retries', 3)
        self.error_history = []
        
    def attempt_fix(self, error_message: str, context: str) -> bool:
        """
        Analyze error and attempt to fix it automatically
        Returns True if fix was successful, False otherwise
        """
        try:
            logger.info(f"🔧 Attempting self-heal for error: {error_message[:100]}...")
            
            # Log error for pattern analysis
            self._log_error(error_message, context)
            
            # Check if we've seen this error before
            cached_fix = self._find_cached_fix(error_message)
            if cached_fix:
                logger.info("Found cached fix, applying...")
                return self._apply_fix(cached_fix, context)
            
            # Analyze error with LLM
            analysis = self._analyze_error(error_message, context)
            if not analysis:
                logger.warning("Could not analyze error")
                return False
            
            # Generate fix solution
            fix_solution = self._generate_fix(analysis, context)
            if not fix_solution:
                logger.warning("Could not generate fix solution")
                return False
            
            # Apply the fix
            success = self._apply_fix(fix_solution, context)
            
            if success:
                logger.info("✅ Self-healing successful!")
                self._cache_fix(error_message, fix_solution)
            else:
                logger.warning("❌ Fix application failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Self-healer error: {str(e)}")
            return False
    
    def _log_error(self, error_message: str, context: str):
        """Log error for pattern analysis"""
        self.error_history.append({
            'error': error_message,
            'context': context,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        })
        
        # Keep only last 100 errors
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
    
    def _find_cached_fix(self, error_message: str) -> Optional[Dict]:
        """Find previously successful fix for similar error"""
        # Simple fuzzy matching on error messages
        for cached in getattr(self, 'fix_cache', []):
            if self._similar_errors(error_message, cached['error']):
                return cached['fix']
        return None
    
    def _similar_errors(self, error1: str, error2: str) -> bool:
        """Check if two errors are similar enough to use same fix"""
        # Extract key error patterns
        pattern1 = re.sub(r'[\'"].*?[\'"]', '"STR"', error1.lower())
        pattern2 = re.sub(r'[\'"].*?[\'"]', '"STR"', error2.lower())
        
        # Check if core error type matches
        key_words1 = set(pattern1.split())
        key_words2 = set(pattern2.split())
        
        common_words = key_words1 & key_words2
        return len(common_words) >= 3
    
    def _analyze_error(self, error_message: str, context: str) -> Optional[str]:
        """Use LLM to analyze the root cause of the error"""
        try:
            prompt = f"""
Analyze this error from our GitReel AI agent and identify the root cause:

ERROR MESSAGE: {error_message}

CONTEXT: {context}

Provide a concise analysis including:
1. What caused this error?
2. Which component is affected?
3. Is this a temporary/transient error or a permanent failure?
4. What's the best approach to fix it?

Keep the analysis under 200 words.
"""
            
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert debugging assistant for an AI video generation system."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error analysis failed: {str(e)}")
            return None
    
    def _generate_fix(self, analysis: str, context: str) -> Optional[Dict]:
        """Generate a specific fix solution based on error analysis"""
        try:
            prompt = f"""
Based on this error analysis, generate a specific fix:

ANALYSIS: {analysis}
CONTEXT: {context}

Provide a fix solution in JSON format:
{{
    "fix_type": "retry|config_change|skip|alternative_method|resource_cleanup",
    "action": "specific action to take",
    "parameters": {{}},
    "retry_delay_seconds": 0,
    "should_retry": true/false
}}

Examples:
- For network errors: {{"fix_type": "retry", "action": "retry_request", "parameters": {{"max_attempts": 3}}, "retry_delay_seconds": 5, "should_retry": true}}
- For missing files: {{"fix_type": "skip", "action": "skip_step", "parameters": {{"reason": "file_missing"}}, "retry_delay_seconds": 0, "should_retry": false}}
- For API limits: {{"fix_type": "retry", "action": "wait_and_retry", "parameters": {{"wait_time": 60}}, "retry_delay_seconds": 60, "should_retry": true}}

Respond with ONLY the JSON object, no other text.
"""
            
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fix generation specialist. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
            
            fix_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', fix_text, re.DOTALL)
            if json_match:
                import json
                fix_dict = json.loads(json_match.group())
                return fix_dict
            
            return None
            
        except Exception as e:
            logger.error(f"Fix generation failed: {str(e)}")
            return None
    
    def _apply_fix(self, fix_solution: Dict, context: str) -> bool:
        """Apply the generated fix solution"""
        try:
            fix_type = fix_solution.get('fix_type', '')
            action = fix_solution.get('action', '')
            
            logger.info(f"Applying fix: {fix_type} - {action}")
            
            if fix_type == 'retry':
                delay = fix_solution.get('retry_delay_seconds', 0)
                if delay > 0:
                    import time
                    logger.info(f"Waiting {delay} seconds before retry...")
                    time.sleep(delay)
                return True  # Signal that retry should happen
                
            elif fix_type == 'skip':
                logger.info(f"Skipping step: {fix_solution.get('parameters', {}).get('reason', 'unknown')}")
                return True  # Skip is considered a successful handling
                
            elif fix_type == 'config_change':
                # Would need to modify config dynamically
                logger.info("Config change requested (manual intervention may be needed)")
                return False
                
            elif fix_type == 'alternative_method':
                # Would need to implement alternative approaches
                logger.info("Alternative method suggested (requires implementation)")
                return False
                
            elif fix_type == 'resource_cleanup':
                # Clean up temporary files/resources
                self._cleanup_resources()
                return True
                
            else:
                logger.warning(f"Unknown fix type: {fix_type}")
                return False
                
        except Exception as e:
            logger.error(f"Fix application failed: {str(e)}")
            return False
    
    def _cleanup_resources(self):
        """Clean up temporary files and resources"""
        import os
        from pathlib import Path
        
        temp_dirs = ['output/temp', 'output/audio', 'output/videos']
        for temp_dir in temp_dirs:
            path = Path(temp_dir)
            if path.exists():
                try:
                    # Remove old temp files (> 1 hour)
                    import time
                    current_time = time.time()
                    for file_path in path.glob('*'):
                        if file_path.is_file():
                            file_age = current_time - file_path.stat().st_mtime
                            if file_age > 3600:  # 1 hour
                                file_path.unlink()
                                logger.info(f"Cleaned up old temp file: {file_path}")
                except Exception as e:
                    logger.error(f"Cleanup error: {str(e)}")
    
    def _cache_fix(self, error_message: str, fix_solution: Dict):
        """Cache successful fix for future use"""
        if not hasattr(self, 'fix_cache'):
            self.fix_cache = []
        
        self.fix_cache.append({
            'error': error_message,
            'fix': fix_solution,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        })
        
        # Keep only last 50 fixes
        if len(self.fix_cache) > 50:
            self.fix_cache = self.fix_cache[-50:]
    
    def get_health_report(self) -> Dict:
        """Generate a health report of the system"""
        try:
            prompt = """
Analyze the recent error history and provide a health report for the GitReel agent.
Include:
1. Most common error types
2. Success rate of self-healing
3. Recommendations for improving reliability
4. Any patterns that suggest systemic issues

Keep it concise and actionable.
"""
            
            error_summary = "\n".join([
                f"- {e['error'][:100]} ({e['context']})" 
                for e in self.error_history[-10:]
            ])
            
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a system health analyst."},
                    {"role": "user", "content": f"{prompt}\n\nRecent errors:\n{error_summary}"}
                ],
                temperature=0.3,
                max_tokens=400
            )
            
            return {
                'report': response.choices[0].message.content,
                'total_errors': len(self.error_history),
                'fixes_cached': len(getattr(self, 'fix_cache', []))
            }
            
        except Exception as e:
            logger.error(f"Health report generation failed: {str(e)}")
            return {
                'report': "Could not generate health report",
                'total_errors': len(self.error_history),
                'fixes_cached': len(getattr(self, 'fix_cache', []))
            }
