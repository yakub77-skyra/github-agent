# 🎬 GitReel AI Agent

**Autonomous AI-powered GitHub repository video creator for YouTube Shorts, Instagram Reels, and Facebook Reels**

## Overview

GitReel is a powerful AI agent that automatically:
- 🔍 Discovers trending and valuable GitHub repositories daily
- 📝 Generates engaging video scripts using Groq LLM
- 🎙️ Creates professional voiceovers with Microsoft Edge TTS (free)
- 🎬 Produces vertical videos (1080x1920) optimized for social media
- 📤 Uploads to YouTube, Instagram, and Facebook automatically
- 🔧 Self-heals errors and optimizes performance

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Scout     │────▶│ ScriptWriter │────▶│   Voice     │
│  (GitHub)   │     │   (Groq)     │     │ Generator   │
└─────────────┘     └──────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│Distributor  │◀────│   Video      │◀────│   Audio     │
│(YT/IG/FB)   │     │  Producer    │     │   File      │
└─────────────┘     └──────────────┘     └─────────────┘
       │
       ▼
┌─────────────┐
│Self-Healer  │
│  (AI Fix)   │
└─────────────┘
```

## Features

### 🎯 Core Capabilities
- **Multi-strategy repo discovery**: Trending, topic-based, and "old but gold" repositories
- **Viral script generation**: Optimized hooks, clear explanations, strong CTAs
- **Professional voiceover**: Microsoft Edge Neural TTS (completely free)
- **Vertical video format**: 1080x1920 resolution perfect for Shorts/Reels
- **Smooth browser navigation**: Automated GitHub page scrolling and capture
- **Multi-platform distribution**: YouTube Shorts, Instagram Reels, Facebook Reels
- **Self-healing system**: AI-powered error detection and automatic fixes

### 🚀 Tech Stack
- **LLM**: Groq API (llama-3.1-70b-versatile) - Fast and free tier available
- **TTS**: Microsoft Edge TTS - Free, high-quality neural voices
- **Browser Automation**: Playwright with Chromium
- **Video Processing**: FFmpeg for professional encoding
- **Hosting**: GitHub Actions (unlimited minutes for public repos)
- **Distribution**: 
  - YouTube: Official API
  - Instagram & Facebook: Zerino API (free third-party service)

## Setup Instructions

### 1. Fork this Repository
```bash
git clone https://github.com/YOUR_USERNAME/gitreel-agent.git
cd gitreel-agent
```

### 2. Configure GitHub Secrets

Go to your repository settings → Secrets and variables → Actions → New repository secret

Add these secrets:

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `GROQ_API_KEY` | Groq API key for LLM | [Get free key at groq.com](https://console.groq.com/keys) |
| `YOUTUBE_API_KEY` | YouTube Data API key | [Google Cloud Console](https://console.cloud.google.com/apis/credentials) |
| `ZERNIO_API_KEY` | Zerino API for IG/FB | [Zerino Dashboard](https://zern.io/) |
| `GITHUB_TOKEN` | GitHub personal access token | [GitHub Settings](https://github.com/settings/tokens) |

### 3. Enable GitHub Actions

- Go to Actions tab in your repository
- Enable workflows if disabled
- The workflow runs daily at 8:00 AM UTC automatically

### 4. Manual Trigger (Optional)

You can manually trigger the workflow:
1. Go to Actions tab
2. Select "GitReel AI Agent - Daily Video Generation"
3. Click "Run workflow"
4. Choose branch and click "Run workflow"

## Configuration

### Customize Video Settings

Edit `src/orchestrator.py`:

```python
config = {
    'video_resolution': (1080, 1920),  # Change resolution
    'voice_style': 'en-US-ChristopherNeural',  # Change voice
    'daily_repo_limit': 3,  # Videos per day
    'max_retries': 3,  # Self-heal attempts
}
```

### Available Voice Styles

- `en-US-ChristopherNeural` - Professional male (default)
- `en-US-JennyNeural` - Professional female
- `en-US-GuyNeural` - Energetic male
- `en-US-EricNeural` - Calm documentary
- `en-US-MichelleNeural` - Friendly female

## Output

### Generated Artifacts

After each run, you'll find:
- **Videos**: `output/videos/*.mp4` - Ready to use vertical videos
- **Logs**: `gitreel.log` - Detailed execution logs
- **Audio**: `output/audio/*.mp3` - Voiceover files (temp)

### Download Videos

1. Go to Actions tab
2. Click on the latest workflow run
3. Scroll to "Artifacts" section
4. Download `gitreel-videos-{run_number}`
5. Extract and upload to your social platforms

## Video Quality Optimization

The agent creates viral-worthy content by:

1. **Hook-first scripts**: Grabs attention in first 3 seconds
2. **Clear value proposition**: Explains WHY developers should care
3. **Visual storytelling**: Smooth scrolling through key repo sections
4. **Professional audio**: High-quality neural voiceover
5. **Platform optimization**: Different captions/tags for each platform
6. **SEO-friendly metadata**: Optimized titles, descriptions, hashtags

## Troubleshooting

### Common Issues

**Workflow fails immediately:**
- Check all secrets are configured correctly
- Verify GitHub token has `repo` scope
- Check Groq API key is active

**Video generation fails:**
- Check logs for specific error messages
- Ensure ffmpeg is installed (handled automatically)
- Verify repository URLs are accessible

**Upload fails:**
- YouTube: Check API quota and authentication
- Instagram/Facebook: Verify Zerino API key is valid
- Check video file size meets platform limits

**Self-healing not working:**
- Review error patterns in logs
- Some errors require manual intervention
- Check Groq API availability

### View Logs

Download the `gitreel-logs` artifact from Actions to see detailed execution logs.

## Customization

### Add More Topics

Edit `src/scout.py` to add more tech topics:

```python
tech_topics = ['your-topic', 'another-topic', ...]
```

### Change Upload Schedule

Edit `.github/workflows/daily_video_generation.yml`:

```yaml
schedule:
  - cron: '0 8 * * *'  # Change cron expression
```

### Modify Script Style

Edit the system prompt in `src/scriptwriter.py` to change the tone and style.

## Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| Groq API | Free | ~1000 requests/day on free tier |
| Edge TTS | Free | Completely free |
| GitHub Actions | Free | Unlimited for public repos |
| YouTube API | Free | 10,000 units/day quota |
| Zerino API | Free | Third-party service |

**Total: $0/month** 🎉

## Roadmap

- [ ] Add subtitle generation and burning
- [ ] Support for running actual code demos
- [ ] Multi-language voice support
- [ ] Custom thumbnail generation
- [ ] Analytics tracking for video performance
- [ ] Discord/Slack notifications
- [ ] Web dashboard for monitoring

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - Feel free to use for personal or commercial projects.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for troubleshooting

---

**Made with ❤️ for the developer community**

Star ⭐ this repo if you find it useful!
