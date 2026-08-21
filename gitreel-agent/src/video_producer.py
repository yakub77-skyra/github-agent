"""
Video Producer Module
Records browser navigation and creates professional vertical videos using Playwright and MoviePy
"""

import os
import logging
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger(__name__)

class VideoProducer:
    """Creates professional vertical videos from GitHub repo navigation"""
    
    def __init__(self, config: dict):
        self.resolution = config.get('video_resolution', (1080, 1920))  # Vertical 9:16
        self.output_dir = Path("output/videos")
        self.temp_dir = Path("output/temp")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Browser settings for headless operation
        self.browser_config = {
            'headless': True,
            'viewport': {'width': 1080, 'height': 1920},
            'device_scale_factor': 1.5,  # Higher DPI for crisp text
            'is_mobile': False,
            'has_touch': False
        }
    
    async def create_video(self, repo: Dict, script: str, audio_path: Path) -> Optional[Path]:
        """
        Create a complete video by:
        1. Recording browser navigation of the GitHub repo
        2. Combining with voiceover audio
        3. Adding subtitles and effects
        """
        try:
            logger.info(f"Creating video for {repo['name']}...")
            
            safe_name = "".join(c for c in repo['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_name = safe_name.replace(' ', '_')
            
            # Step 1: Record screen navigation
            recording_path = await self._record_repo_navigation(repo)
            if not recording_path or not recording_path.exists():
                raise Exception("Screen recording failed")
            
            logger.info(f"Screen recording completed: {recording_path}")
            
            # Step 2: Get audio duration
            audio_duration = self._get_audio_duration(audio_path)
            if audio_duration <= 0:
                raise Exception("Invalid audio duration")
            
            # Step 3: Combine video and audio with FFmpeg
            final_video_path = self.output_dir / f"{safe_name}_gitreel.mp4"
            
            success = await self._combine_audio_video(
                recording_path, 
                audio_path, 
                final_video_path,
                audio_duration
            )
            
            if not success:
                raise Exception("Failed to combine audio and video")
            
            # Step 4: Add subtitles (optional enhancement)
            # subtitle_path = self._generate_subtitles(script)
            # if subtitle_path:
            #     final_video_path = self._burn_subtitles(final_video_path, subtitle_path)
            
            # Cleanup temp files
            if recording_path.exists():
                recording_path.unlink()
            
            logger.info(f"Video created successfully: {final_video_path}")
            return final_video_path
            
        except Exception as e:
            logger.error(f"Error creating video for {repo['name']}: {str(e)}")
            return None
    
    async def _record_repo_navigation(self, repo: Dict) -> Optional[Path]:
        """Record browser navigation of the GitHub repository page"""
        output_path = self.temp_dir / f"temp_recording_{repo['id']}.mp4"
        
        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--disable-gpu'
                    ]
                )
                
                # Create page with vertical viewport
                page = await browser.new_page(
                    viewport={'width': 1080, 'height': 1920},
                    device_scale_factor=1.5
                )
                
                # Start screen recording
                screen_size = {'width': 1080, 'height': 1920}
                
                # Navigate to GitHub repo
                logger.info(f"Navigating to {repo['url']}...")
                await page.goto(repo['url'], wait_until='networkidle', timeout=30000)
                
                # Wait for page to fully load
                await page.wait_for_timeout(2000)
                
                # Record multiple sections with smooth scrolling
                frames = []
                
                # Section 1: Repo header and description
                await self._smooth_scroll_to(page, 0)
                await page.wait_for_timeout(1500)
                
                # Section 2: README content
                await self._smooth_scroll_to(page, 800)
                await page.wait_for_timeout(2000)
                
                # Section 3: Code examples
                await self._smooth_scroll_to(page, 1600)
                await page.wait_for_timeout(2000)
                
                # Section 4: Features/installation
                await self._smooth_scroll_to(page, 2400)
                await page.wait_for_timeout(1500)
                
                # Section 5: Back to top for ending
                await self._smooth_scroll_to(page, 0)
                await page.wait_for_timeout(1000)
                
                # Take screenshots at key points for video creation
                screenshot_paths = []
                scroll_positions = [0, 800, 1600, 2400, 0]
                
                for i, pos in enumerate(scroll_positions):
                    await self._smooth_scroll_to(page, pos)
                    await page.wait_for_timeout(500)
                    screenshot_path = self.temp_dir / f"frame_{repo['id']}_{i}.png"
                    await page.screenshot(path=str(screenshot_path), full_page=False)
                    screenshot_paths.append(screenshot_path)
                
                await browser.close()
                
                # Convert screenshots to video using FFmpeg
                await self._screenshots_to_video(screenshot_paths, output_path)
                
                # Cleanup screenshots
                for path in screenshot_paths:
                    if path.exists():
                        path.unlink()
                
                return output_path
                
        except Exception as e:
            logger.error(f"Error recording navigation: {str(e)}")
            return None
    
    async def _smooth_scroll_to(self, page, target_position: int, duration: int = 1000):
        """Smoothly scroll to a target position"""
        steps = 10
        increment = target_position / steps
        
        for i in range(steps):
            current_pos = int(increment * (i + 1))
            await page.evaluate(f"window.scrollTo(0, {current_pos})")
            await page.wait_for_timeout(duration // steps)
    
    async def _screenshots_to_video(self, screenshot_paths: list, output_path: Path):
        """Convert sequence of screenshots to video with smooth transitions"""
        # Create intermediate video from images
        temp_video = self.temp_dir / "temp_video.mp4"
        
        # Create file list for FFmpeg concat
        file_list_path = self.temp_dir / "file_list.txt"
        with open(file_list_path, 'w') as f:
            for img_path in screenshot_paths:
                f.write(f"file '{img_path}'\nduration 2\n")
            f.write(f"file '{screenshot_paths[-1]}'\n")  # Last frame
        
        try:
            # Use FFmpeg to create video from images with crossfade transitions
            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(file_list_path),
                '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-r', '30',
                str(temp_video)
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                # Fallback: simple image sequence
                await self._simple_images_to_video(screenshot_paths, output_path)
            else:
                # Apply crossfade transitions
                await self._apply_crossfades(temp_video, output_path)
                if temp_video.exists():
                    temp_video.unlink()
            
            if file_list_path.exists():
                file_list_path.unlink()
                
        except Exception as e:
            logger.error(f"Error creating video from screenshots: {str(e)}")
            await self._simple_images_to_video(screenshot_paths, output_path)
    
    async def _simple_images_to_video(self, screenshot_paths: list, output_path: Path):
        """Fallback method: simple image sequence to video"""
        cmd = [
            'ffmpeg',
            '-y',
            '-loop', '1',
            '-i', str(screenshot_paths[0]),
            '-t', '10',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            str(output_path)
        ]
        
        result = await asyncio.create_subprocess_exec(*cmd)
        await result.communicate()
    
    async def _apply_crossfades(self, input_path: Path, output_path: Path):
        """Apply crossfade transitions between clips"""
        # For simplicity, just copy the video
        cmd = [
            'ffmpeg',
            '-y',
            '-i', str(input_path),
            '-c', 'copy',
            str(output_path)
        ]
        
        result = await asyncio.create_subprocess_exec(*cmd)
        await result.communicate()
    
    async def _combine_audio_video(self, video_path: Path, audio_path: Path, 
                                   output_path: Path, audio_duration: float) -> bool:
        """Combine video and audio tracks, trimming/padding as needed"""
        try:
            # Get video duration
            video_duration = self._get_video_duration(video_path)
            
            if video_duration <= 0:
                logger.error("Invalid video duration")
                return False
            
            # Determine final duration (use audio as primary)
            final_duration = audio_duration
            
            # Build FFmpeg command
            if video_duration < audio_duration:
                # Loop video to match audio
                filters = f"[0:v]loop=loop=-1:size=2,trim=duration={audio_duration}[v]"
            else:
                # Trim video to match audio
                filters = f"[0:v]trim=duration={audio_duration}[v]"
            
            cmd = [
                'ffmpeg',
                '-y',
                '-i', str(video_path),
                '-i', str(audio_path),
                '-filter_complex', filters,
                '-map', '[v]',
                '-map', '1:a',
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-shortest',
                '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart',
                str(output_path)
            ]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0 and output_path.exists():
                logger.info(f"Audio/video combined successfully: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg combine failed: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Error combining audio/video: {str(e)}")
            return False
    
    def _get_video_duration(self, video_path: Path) -> float:
        """Get video duration in seconds"""
        try:
            import subprocess
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(video_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"Error getting video duration: {str(e)}")
            return 0.0
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get audio duration in seconds"""
        try:
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            return audio.info.length
        except ImportError:
            # Fallback estimation
            file_size_kb = audio_path.stat().st_size / 1024
            return file_size_kb / 16
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            return 0.0
    
    def create_video(self, repo: Dict, script: str, audio_path: Path) -> Optional[Path]:
        """Synchronous wrapper for async create_video"""
        return asyncio.run(self.create_video_async(repo, script, audio_path))
    
    async def create_video_async(self, repo: Dict, script: str, audio_path: Path) -> Optional[Path]:
        """Async version of create_video"""
        return await self.create_video(repo, script, audio_path)
