"""
Multi-Platform Distributor Module
Uploads videos to YouTube, Instagram, and Facebook using official APIs and Zerino
"""

import os
import logging
import requests
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MultiPlatformDistributor:
    """Handles video distribution to YouTube, Instagram, and Facebook"""
    
    def __init__(self, config: dict):
        self.youtube_api_key = config.get('youtube_api_key')
        self.zernio_api_key = config.get('zernio_api_key')
        self.zernio_base_url = "https://api.zern.io/v1"  # Placeholder - update with actual API
        
    def upload_to_youtube(self, video_path: Path, repo: Dict) -> Dict:
        """
        Upload video to YouTube Shorts using official API
        Returns upload result with video ID and status
        """
        try:
            logger.info(f"Uploading {repo['name']} to YouTube Shorts...")
            
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.oauth2.credentials import Credentials
            
            # Prepare video metadata optimized for Shorts
            title = self._generate_youtube_title(repo)
            description = self._generate_youtube_description(repo)
            tags = self._generate_youtube_tags(repo)
            
            # Create YouTube API client
            youtube = build('youtube', 'v3', developerKey=self.youtube_api_key)
            
            # Prepare request body
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],
                    'tags': tags,
                    'categoryId': '28'  # Science & Technology
                },
                'status': {
                    'privacyStatus': 'public',
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Upload video
            media = MediaFileUpload(
                str(video_path),
                mimetype='video/mp4',
                chunksize=1024*1024,  # 1MB chunks
                resumable=True
            )
            
            request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    logger.info(f"Uploaded {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/shorts/{video_id}"
            
            logger.info(f"YouTube upload successful: {video_url}")
            
            return {
                'success': True,
                'platform': 'youtube',
                'video_id': video_id,
                'video_url': video_url,
                'title': title,
                'uploaded_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {str(e)}")
            return {
                'success': False,
                'platform': 'youtube',
                'error': str(e),
                'uploaded_at': datetime.utcnow().isoformat()
            }
    
    def upload_to_instagram(self, video_path: Path, repo: Dict) -> Dict:
        """
        Upload video to Instagram Reels using Zerino API
        Returns upload result with status
        """
        try:
            logger.info(f"Uploading {repo['name']} to Instagram Reels via Zerino...")
            
            # Prepare caption optimized for Instagram
            caption = self._generate_instagram_caption(repo)
            
            # Zerino API endpoint for Instagram Reels
            endpoint = f"{self.zernio_base_url}/instagram/reels"
            
            headers = {
                'Authorization': f'Bearer {self.zernio_api_key}',
                'Accept': 'application/json'
            }
            
            # Prepare files and data
            files = {
                'video': ('video.mp4', open(str(video_path), 'rb'), 'video/mp4')
            }
            
            data = {
                'caption': caption,
                'thumbnail': None  # Optional thumbnail
            }
            
            response = requests.post(
                endpoint,
                headers=headers,
                files=files,
                data=data,
                timeout=300  # 5 minute timeout for upload
            )
            
            # Close file handle
            files['video'][1].close()
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Instagram upload successful: {result.get('url', 'N/A')}")
                
                return {
                    'success': True,
                    'platform': 'instagram',
                    'media_id': result.get('id', 'unknown'),
                    'video_url': result.get('url', 'N/A'),
                    'caption': caption,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"Zerino API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'platform': 'instagram',
                    'error': error_msg,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Instagram upload failed: {str(e)}")
            return {
                'success': False,
                'platform': 'instagram',
                'error': str(e),
                'uploaded_at': datetime.utcnow().isoformat()
            }
    
    def upload_to_facebook(self, video_path: Path, repo: Dict) -> Dict:
        """
        Upload video to Facebook Reels using Zerino API
        Returns upload result with status
        """
        try:
            logger.info(f"Uploading {repo['name']} to Facebook Reels via Zerino...")
            
            # Prepare caption optimized for Facebook
            caption = self._generate_facebook_caption(repo)
            
            # Zerino API endpoint for Facebook Reels
            endpoint = f"{self.zernio_base_url}/facebook/reels"
            
            headers = {
                'Authorization': f'Bearer {self.zernio_api_key}',
                'Accept': 'application/json'
            }
            
            # Prepare files and data
            files = {
                'video': ('video.mp4', open(str(video_path), 'rb'), 'video/mp4')
            }
            
            data = {
                'caption': caption,
                'privacy': 'PUBLIC'  # or 'FRIENDS', 'ONLY_ME'
            }
            
            response = requests.post(
                endpoint,
                headers=headers,
                files=files,
                data=data,
                timeout=300
            )
            
            # Close file handle
            files['video'][1].close()
            
            if response.status_code in [200, 201]:
                result = response.json()
                logger.info(f"Facebook upload successful: {result.get('url', 'N/A')}")
                
                return {
                    'success': True,
                    'platform': 'facebook',
                    'media_id': result.get('id', 'unknown'),
                    'video_url': result.get('url', 'N/A'),
                    'caption': caption,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"Zerino API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    'success': False,
                    'platform': 'facebook',
                    'error': error_msg,
                    'uploaded_at': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Facebook upload failed: {str(e)}")
            return {
                'success': False,
                'platform': 'facebook',
                'error': str(e),
                'uploaded_at': datetime.utcnow().isoformat()
            }
    
    def _generate_youtube_title(self, repo: Dict) -> str:
        """Generate engaging YouTube Shorts title"""
        name = repo['name'].split('/')[-1]
        stars = repo['stars']
        
        titles = [
            f"This GitHub Repo Has {stars:,} Stars! 🚀 | {name}",
            f"{name}: The GitHub Repo You NEED to Know! ⭐",
            f"I Found the PERFECT GitHub Repo for Developers! 💻 | {name}",
            f"Why {stars:,} Developers Starred This Repo 🔥 | {name}",
            f"This GitHub Repo Will Change How You Code! 🎯 | {name}"
        ]
        
        # Pick title based on star count for variety
        if stars > 10000:
            return titles[3]
        elif stars > 5000:
            return titles[0]
        elif stars > 1000:
            return titles[1]
        else:
            return titles[4]
    
    def _generate_youtube_description(self, repo: Dict) -> str:
        """Generate YouTube description with SEO optimization"""
        name = repo['name']
        url = repo['url']
        description = repo.get('description', 'Amazing GitHub repository')
        
        return f"""🔥 Check out this amazing GitHub repository: {name}

{description}

⭐ Repository: {url}

💡 Why you should check this out:
- High-quality open source project
- Active community and maintenance
- Perfect for developers looking to level up

👇 What's your favorite GitHub repo? Comment below!

#GitHub #OpenSource #Programming #Coding #Developer #Tech #Shorts
""".strip()
    
    def _generate_youtube_tags(self, repo: Dict) -> list:
        """Generate YouTube tags for better discoverability"""
        base_tags = ['github', 'open source', 'programming', 'coding', 'developer', 'tech']
        
        # Add language-specific tags
        if repo.get('language'):
            base_tags.append(repo['language'].lower())
        
        # Add topic tags
        for topic in repo.get('topics', [])[:5]:
            base_tags.append(topic.lower().replace('-', ''))
        
        base_tags.extend(['software development', 'code review', 'tech tips'])
        
        return base_tags
    
    def _generate_instagram_caption(self, repo: Dict) -> str:
        """Generate Instagram-optimized caption with hashtags"""
        name = repo['name'].split('/')[-1]
        stars = repo['stars']
        description = repo.get('description', '')[:100]
        
        return f"""🚀 {name} - {stars:,} ⭐

{description}...

This repo is a game-changer for developers! 💻

Link in bio to check it out! 👆

#github #opensource #programming #coding #developer #tech #python #javascript #webdev #softwaredeveloper #codelife #techreels #programmerlife #codinglife
""".strip()
    
    def _generate_facebook_caption(self, repo: Dict) -> str:
        """Generate Facebook-optimized caption"""
        name = repo['name'].split('/')[-1]
        stars = repo['stars']
        url = repo['url']
        
        return f"""🔥 Amazing GitHub Find Alert! 

{name} has {stars:,} stars and counting! ⭐

Perfect for developers who want to level up their skills. Check it out: {url}

Share with your dev friends! 👇

#GitHub #Programming #OpenSource #Tech #Developers
""".strip()
