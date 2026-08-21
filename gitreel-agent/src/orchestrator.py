"""
GitReel AI Agent - Main Orchestrator
Coordinates all modules for autonomous GitHub repo video creation and distribution
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Import our modules
from scout import GitHubScout
from scriptwriter import ScriptWriter
from voice_generator import VoiceGenerator
from video_producer import VideoProducer
from distributor import MultiPlatformDistributor
from self_healer import SelfHealer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gitreel.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GitReelAgent:
    """Main orchestrator for the GitReel AI Agent"""
    
    def __init__(self):
        self.config = self.load_config()
        self.scout = GitHubScout(self.config)
        self.scriptwriter = ScriptWriter(self.config)
        self.voice_generator = VoiceGenerator(self.config)
        self.video_producer = VideoProducer(self.config)
        self.distributor = MultiPlatformDistributor(self.config)
        self.self_healer = SelfHealer(self.config)
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def load_config(self):
        """Load configuration from environment variables and config file"""
        config = {
            'groq_api_key': os.getenv('GROQ_API_KEY'),
            'youtube_api_key': os.getenv('YOUTUBE_API_KEY'),
            'zernio_api_key': os.getenv('ZERNIO_API_KEY'),
            'github_token': os.getenv('GITHUB_TOKEN'),
            'video_resolution': (1080, 1920),  # Vertical for Reels/Shorts
            'voice_style': 'en-US-ChristopherNeural',  # Professional male voice
            'max_retries': 3,
            'daily_repo_limit': 3,
        }
        
        # Validate required credentials
        required = ['groq_api_key', 'youtube_api_key', 'zernio_api_key', 'github_token']
        missing = [key for key in required if not config.get(key)]
        if missing:
            raise ValueError(f"Missing required credentials: {missing}")
            
        return config
    
    def run_daily_workflow(self):
        """Execute the complete daily workflow with error handling"""
        logger.info("🚀 Starting GitReel Daily Workflow")
        workflow_start = datetime.now()
        
        try:
            # Step 1: Discover trending repositories
            logger.info("🔍 Step 1: Scouting trending GitHub repositories...")
            repos = self.scout.discover_trending_repos()
            if not repos:
                logger.warning("No trending repositories found")
                return False
                
            logger.info(f"Found {len(repos)} trending repositories")
            
            # Step 2: Process each repository
            successful_videos = []
            for i, repo in enumerate(repos[:self.config['daily_repo_limit']], 1):
                logger.info(f"\n📝 Processing repository {i}/{min(len(repos), self.config['daily_repo_limit'])}: {repo['name']}")
                
                try:
                    video_path = self.process_repository(repo)
                    if video_path:
                        successful_videos.append({
                            'repo': repo,
                            'video_path': video_path
                        })
                except Exception as e:
                    logger.error(f"Failed to process {repo['name']}: {str(e)}")
                    # Attempt self-healing
                    healed = self.self_healer.attempt_fix(str(e), "repository_processing")
                    if healed:
                        logger.info("Self-healing successful, retrying...")
                        try:
                            video_path = self.process_repository(repo)
                            if video_path:
                                successful_videos.append({
                                    'repo': repo,
                                    'video_path': video_path
                                })
                        except Exception as retry_error:
                            logger.error(f"Retry failed for {repo['name']}: {str(retry_error)}")
            
            # Step 3: Distribute videos to platforms
            if successful_videos:
                logger.info("\n📤 Step 3: Distributing videos to platforms...")
                distribution_results = self.distribute_videos(successful_videos)
                
                # Step 4: Final review and optimization
                logger.info("\n🔍 Step 4: Performing final quality review...")
                self.final_review(successful_videos, distribution_results)
                
                logger.info(f"\n✅ Daily workflow completed successfully!")
                logger.info(f"Created and distributed {len(successful_videos)} videos")
                return True
            else:
                logger.error("No successful videos created")
                return False
                
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            # Critical error - attempt full system heal
            self.self_healer.attempt_fix(str(e), "critical_workflow_failure")
            return False
            
        finally:
            workflow_end = datetime.now()
            duration = workflow_end - workflow_start
            logger.info(f"Total workflow duration: {duration}")
    
    def process_repository(self, repo):
        """Process a single repository through the entire pipeline"""
        try:
            # Generate script using LLM
            logger.info(f"  📝 Generating script for {repo['name']}...")
            script = self.scriptwriter.generate_script(repo)
            if not script:
                raise Exception("Failed to generate script")
            
            # Generate voiceover
            logger.info(f"  🎙️ Generating voiceover for {repo['name']}...")
            audio_path = self.voice_generator.generate_voiceover(script, repo['name'])
            if not audio_path or not audio_path.exists():
                raise Exception("Failed to generate voiceover")
            
            # Record and produce video
            logger.info(f"  🎬 Producing video for {repo['name']}...")
            video_path = self.video_producer.create_video(repo, script, audio_path)
            if not video_path or not video_path.exists():
                raise Exception("Failed to create video")
            
            logger.info(f"  ✅ Video created: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"Error processing {repo['name']}: {str(e)}")
            raise
    
    def distribute_videos(self, successful_videos):
        """Distribute videos to all platforms"""
        results = {
            'youtube': [],
            'instagram': [],
            'facebook': []
        }
        
        for video_data in successful_videos:
            repo = video_data['repo']
            video_path = video_data['video_path']
            
            # YouTube Shorts
            try:
                yt_result = self.distributor.upload_to_youtube(video_path, repo)
                results['youtube'].append(yt_result)
                logger.info(f"  ✅ Uploaded to YouTube: {repo['name']}")
            except Exception as e:
                logger.error(f"  ❌ YouTube upload failed for {repo['name']}: {str(e)}")
                results['youtube'].append({'success': False, 'error': str(e)})
            
            # Instagram Reels via Zerino
            try:
                ig_result = self.distributor.upload_to_instagram(video_path, repo)
                results['instagram'].append(ig_result)
                logger.info(f"  ✅ Uploaded to Instagram: {repo['name']}")
            except Exception as e:
                logger.error(f"  ❌ Instagram upload failed for {repo['name']}: {str(e)}")
                results['instagram'].append({'success': False, 'error': str(e)})
            
            # Facebook Reels via Zerino
            try:
                fb_result = self.distributor.upload_to_facebook(video_path, repo)
                results['facebook'].append(fb_result)
                logger.info(f"  ✅ Uploaded to Facebook: {repo['name']}")
            except Exception as e:
                logger.error(f"  ❌ Facebook upload failed for {repo['name']}: {str(e)}")
                results['facebook'].append({'success': False, 'error': str(e)})
        
        return results
    
    def final_review(self, successful_videos, distribution_results):
        """Perform final quality review and optimization"""
        logger.info("Performing AI-powered quality review...")
        
        review_summary = {
            'total_videos': len(successful_videos),
            'youtube_success': sum(1 for r in distribution_results['youtube'] if r.get('success', False)),
            'instagram_success': sum(1 for r in distribution_results['instagram'] if r.get('success', False)),
            'facebook_success': sum(1 for r in distribution_results['facebook'] if r.get('success', False)),
        }
        
        # Generate review report using LLM
        review_prompt = f"""
        Review the following GitReel agent performance:
        - Videos created: {review_summary['total_videos']}
        - YouTube uploads successful: {review_summary['youtube_success']}/{review_summary['total_videos']}
        - Instagram uploads successful: {review_summary['instagram_success']}/{review_summary['total_videos']}
        - Facebook uploads successful: {review_summary['facebook_success']}/{review_summary['total_videos']}
        
        Provide specific recommendations to improve video quality and viral potential.
        Focus on algorithm optimization for Shorts/Reels.
        """
        
        try:
            review_report = self.scriptwriter.llm_client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": review_prompt}],
                max_tokens=500
            )
            logger.info(f"\n📊 AI Review Report:\n{review_report.choices[0].message.content}")
        except Exception as e:
            logger.warning(f"Could not generate AI review: {str(e)}")
        
        logger.info(f"\n📈 Distribution Summary:")
        logger.info(f"  YouTube: {review_summary['youtube_success']}/{review_summary['total_videos']} successful")
        logger.info(f"  Instagram: {review_summary['instagram_success']}/{review_summary['total_videos']} successful")
        logger.info(f"  Facebook: {review_summary['facebook_success']}/{review_summary['total_videos']} successful")

def main():
    """Main entry point"""
    try:
        agent = GitReelAgent()
        success = agent.run_daily_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
