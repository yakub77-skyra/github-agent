"""
GitHub Scout Module
Discovers trending and useful GitHub repositories using GitHub API
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class GitHubScout:
    """Discovers trending and valuable GitHub repositories"""
    
    def __init__(self, config: dict):
        self.github_token = config.get('github_token')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def discover_trending_repos(self) -> List[Dict]:
        """
        Discover trending repositories using multiple strategies:
        1. GitHub Trending API (via scraping alternative)
        2. Most starred repos in last 24h/week
        3. Popular topics and tags
        4. Old but still useful repos (high star/fork ratio)
        """
        all_repos = []
        
        # Strategy 1: Recently trending (last 24 hours)
        logger.info("Fetching recently trending repositories...")
        recent_repos = self._get_trending_by_timeframe('daily')
        all_repos.extend(recent_repos)
        
        # Strategy 2: Weekly trending
        logger.info("Fetching weekly trending repositories...")
        weekly_repos = self._get_trending_by_timeframe('weekly')
        all_repos.extend(weekly_repos)
        
        # Strategy 3: Popular tech topics
        tech_topics = ['machine-learning', 'python', 'javascript', 'react', 
                      'ai', 'docker', 'kubernetes', 'typescript', 'nextjs',
                      'fastapi', 'rust', 'go', 'vue', 'svelte', 'tailwindcss']
        
        logger.info(f"Fetching repos from {len(tech_topics)} tech topics...")
        for topic in tech_topics:
            topic_repos = self._get_repos_by_topic(topic)
            all_repos.extend(topic_repos)
        
        # Strategy 4: Old but gold repos (high quality, maintained)
        logger.info("Finding old but valuable repositories...")
        old_gold_repos = self._find_old_but_valuable_repos()
        all_repos.extend(old_gold_repos)
        
        # Remove duplicates and sort by score
        unique_repos = self._deduplicate_and_score(all_repos)
        
        logger.info(f"Total unique repositories found: {len(unique_repos)}")
        return unique_repos[:20]  # Return top 20 for further processing
    
    def _get_trending_by_timeframe(self, timeframe: str) -> List[Dict]:
        """Get trending repositories by timeframe (daily/weekly)"""
        try:
            since = datetime.utcnow() - timedelta(days=1 if timeframe == 'daily' else 7)
            since_str = since.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            query = f"created:>={since_str} stars:>100 language:Python OR language:JavaScript OR language:TypeScript"
            
            url = f"{self.base_url}/search/repositories"
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            repos = response.json().get('items', [])
            return [self._format_repo_data(repo, 'trending') for repo in repos]
            
        except Exception as e:
            logger.error(f"Error fetching {timeframe} trending repos: {str(e)}")
            return []
    
    def _get_repos_by_topic(self, topic: str) -> List[Dict]:
        """Get repositories by topic/tag"""
        try:
            url = f"{self.base_url}/search/repositories"
            query = f"topic:{topic} stars:>50 push:>2024-01-01"
            
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': 5
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            repos = response.json().get('items', [])
            return [self._format_repo_data(repo, 'topic') for repo in repos]
            
        except Exception as e:
            logger.error(f"Error fetching repos for topic {topic}: {str(e)}")
            return []
    
    def _find_old_but_valuable_repos(self) -> List[Dict]:
        """Find old repositories that are still valuable and maintained"""
        try:
            # Look for repos created before 2022 but recently updated and highly starred
            url = f"{self.base_url}/search/repositories"
            query = "created:<2022-01-01 pushed:>2024-11-01 stars:>500"
            
            params = {
                'q': query,
                'sort': 'updated',
                'order': 'desc',
                'per_page': 10
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            
            repos = response.json().get('items', [])
            return [self._format_repo_data(repo, 'old_gold') for repo in repos]
            
        except Exception as e:
            logger.error(f"Error finding old but valuable repos: {str(e)}")
            return []
    
    def _format_repo_data(self, repo_data: dict, source: str) -> Dict:
        """Format repository data for our pipeline"""
        return {
            'id': repo_data['id'],
            'name': repo_data['full_name'],
            'description': repo_data.get('description', '') or 'No description available',
            'url': repo_data['html_url'],
            'clone_url': repo_data['clone_url'],
            'stars': repo_data['stargazers_count'],
            'forks': repo_data['forks_count'],
            'language': repo_data.get('language', 'Unknown'),
            'topics': repo_data.get('topics', []),
            'created_at': repo_data['created_at'],
            'updated_at': repo_data['updated_at'],
            'source': source,
            'score': self._calculate_repo_score(repo_data),
            'owner': repo_data['owner']['login'],
            'readme_url': f"https://raw.githubusercontent.com/{repo_data['full_name']}/main/README.md"
        }
    
    def _calculate_repo_score(self, repo_data: dict) -> float:
        """Calculate a score for repository prioritization"""
        stars = repo_data['stargazers_count']
        forks = repo_data['forks_count']
        age_days = (datetime.utcnow() - datetime.strptime(repo_data['created_at'], '%Y-%m-%dT%H:%M:%SZ')).days
        
        # Score components
        star_score = min(stars / 1000, 50)  # Max 50 points from stars
        fork_score = min(forks / 100, 20)   # Max 20 points from forks
        
        # Bonus for recent activity
        updated_recently = datetime.strptime(repo_data['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        days_since_update = (datetime.utcnow() - updated_recently).days
        activity_score = max(0, 15 - days_since_update / 2)  # Max 15 points
        
        # Bonus for good documentation (has README)
        readme_score = 10 if repo_data.get('has_pages', True) else 0
        
        # Penalty for very old inactive repos
        age_penalty = min(age_days / 365, 5) if days_since_update > 90 else 0
        
        total_score = star_score + fork_score + activity_score + readme_score - age_penalty
        return max(0, total_score)
    
    def _deduplicate_and_score(self, repos: List[Dict]) -> List[Dict]:
        """Remove duplicates and sort by score"""
        seen_ids = set()
        unique_repos = []
        
        for repo in repos:
            if repo['id'] not in seen_ids:
                seen_ids.add(repo['id'])
                unique_repos.append(repo)
        
        # Sort by score descending
        unique_repos.sort(key=lambda x: x['score'], reverse=True)
        return unique_repos
    
    def fetch_readme(self, repo: Dict) -> Optional[str]:
        """Fetch README content for a repository"""
        try:
            readme_urls = [
                f"https://raw.githubusercontent.com/{repo['name']}/main/README.md",
                f"https://raw.githubusercontent.com/{repo['name']}/master/README.md",
                f"https://raw.githubusercontent.com/{repo['name']}/main/readme.md",
                f"https://raw.githubusercontent.com/{repo['name']}/master/readme.md"
            ]
            
            for url in readme_urls:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
            
            logger.warning(f"No README found for {repo['name']}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching README for {repo['name']}: {str(e)}")
            return None
