"""
Voice Generator Module
Uses Microsoft Edge TTS (free) to generate professional voiceovers
"""

import os
import logging
import asyncio
from pathlib import Path
from typing import Optional
import edge_tts
from edge_tts import SubMaker

logger = logging.getLogger(__name__)

class VoiceGenerator:
    """Generates professional voiceovers using Microsoft Edge TTS (free)"""
    
    def __init__(self, config: dict):
        self.voice_style = config.get('voice_style', 'en-US-ChristopherNeural')
        self.output_dir = Path("output/audio")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Professional voice options for different styles
        self.voices = {
            'professional_male': 'en-US-ChristopherNeural',
            'professional_female': 'en-US-JennyNeural',
            'energetic_male': 'en-US-GuyNeural',
            'calm_documentary': 'en-US-EricNeural',
            'friendly': 'en-US-MichelleNeural'
        }
    
    def generate_voiceover(self, script: str, repo_name: str) -> Optional[Path]:
        """
        Generate voiceover audio from script using Edge TTS
        Returns path to the generated audio file
        """
        try:
            logger.info(f"Generating voiceover for {repo_name}...")
            
            # Clean the script (remove any markdown or special characters)
            clean_script = self._clean_script(script)
            
            # Output file path
            safe_name = "".join(c for c in repo_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            output_path = self.output_dir / f"{safe_name.replace(' ', '_')}_voiceover.mp3"
            
            # Generate audio using Edge TTS
            asyncio.run(self._generate_audio(clean_script, output_path))
            
            if output_path.exists() and output_path.stat().st_size > 0:
                duration = self._get_audio_duration(output_path)
                logger.info(f"Voiceover generated: {output_path} ({duration:.2f}s)")
                return output_path
            else:
                logger.error(f"Generated audio file is empty or missing: {output_path}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating voiceover for {repo_name}: {str(e)}")
            return None
    
    async def _generate_audio(self, text: str, output_path: Path):
        """Async function to generate audio using Edge TTS"""
        try:
            communicate = edge_tts.Communicate(text, self.voice_style)
            await communicate.save(str(output_path))
        except Exception as e:
            logger.error(f"Edge TTS generation failed: {str(e)}")
            raise
    
    def _clean_script(self, script: str) -> str:
        """Clean script for TTS processing"""
        import re
        
        # Remove markdown formatting
        script = re.sub(r'\*\*(.*?)\*\*', r'\1', script)  # Bold
        script = re.sub(r'\*(.*?)\*', r'\1', script)      # Italic
        script = re.sub(r'`(.*?)`', r'\1', script)        # Code
        script = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', script)  # Links
        script = re.sub(r'#{1,6}\s*', '', script)         # Headers
        script = re.sub(r'\n{3,}', '\n\n', script)        # Multiple newlines
        
        # Remove bracketed directions like [Visual:], [Show:], etc.
        script = re.sub(r'\[.*?\]', '', script)
        
        # Clean up whitespace
        script = ' '.join(script.split())
        
        return script
    
    def _get_audio_duration(self, audio_path: Path) -> float:
        """Get duration of audio file in seconds"""
        try:
            # Try using mutagen library if available
            from mutagen.mp3 import MP3
            audio = MP3(str(audio_path))
            return audio.info.length
        except ImportError:
            # Fallback: estimate based on file size (rough approximation)
            # Average MP3 at 128kbps: ~16KB per second
            file_size_kb = audio_path.stat().st_size / 1024
            return file_size_kb / 16
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {str(e)}")
            return 0.0
    
    def adjust_speed_for_timing(self, audio_path: Path, target_duration: float) -> Optional[Path]:
        """
        Adjust audio speed to match target video duration
        Uses ffmpeg to change playback speed
        """
        import subprocess
        
        current_duration = self._get_audio_duration(audio_path)
        if current_duration == 0:
            logger.error("Cannot adjust speed: unknown audio duration")
            return None
        
        speed_factor = current_duration / target_duration
        
        # Clamp speed factor to reasonable range (0.5x to 2.0x)
        speed_factor = max(0.5, min(2.0, speed_factor))
        
        if 0.9 <= speed_factor <= 1.1:
            # No adjustment needed
            return audio_path
        
        output_path = audio_path.parent / f"{audio_path.stem}_adjusted.mp3"
        
        try:
            # Use ffmpeg to adjust speed
            cmd = [
                'ffmpeg', '-i', str(audio_path),
                '-filter:a', f'atempo={speed_factor}',
                '-y', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and output_path.exists():
                logger.info(f"Audio speed adjusted: {speed_factor:.2f}x")
                return output_path
            else:
                logger.error(f"FFmpeg speed adjustment failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error adjusting audio speed: {str(e)}")
            return None
    
    def list_available_voices(self) -> list:
        """List all available Edge TTS voices"""
        try:
            # Run edge-tts --list-voices command
            import subprocess
            result = subprocess.run(['edge-tts', '--list-voices'], 
                                  capture_output=True, text=True)
            voices = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    voices.append(line.strip())
            return voices
        except Exception as e:
            logger.error(f"Error listing voices: {str(e)}")
            return list(self.voices.values())
