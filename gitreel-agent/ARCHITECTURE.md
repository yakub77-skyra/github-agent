# GitReel AI Agent - Complete Project Structure

```
gitreel-agent/
│
├── .github/
│   └── workflows/
│       └── daily_video_generation.yml    # GitHub Actions workflow (runs daily at 8 AM UTC)
│
├── src/
│   ├── __init__.py                      # Package initialization
│   ├── orchestrator.py                  # Main coordinator - runs the entire workflow
│   ├── scout.py                         # Discovers trending GitHub repositories
│   ├── scriptwriter.py                  # Generates viral video scripts using Groq LLM
│   ├── voice_generator.py               # Creates voiceovers with Microsoft Edge TTS
│   ├── video_producer.py                # Records browser & creates vertical videos
│   ├── distributor.py                   # Uploads to YouTube, Instagram, Facebook
│   └── self_healer.py                   # AI-powered error detection and fixing
│
├── .env.example                         # Template for environment variables
├── .gitignore                          # Git ignore rules
├── requirements.txt                    # Python dependencies
├── README.md                           # Full documentation
└── QUICKSTART.md                       # Quick start guide (5 minutes)

OUTPUT STRUCTURE (generated at runtime):
output/
├── videos/                             # Final MP4 files ready for upload
├── audio/                              # Voiceover MP3 files (temporary)
└── temp/                               # Temporary processing files (auto-cleaned)
```

## Module Responsibilities

### 1. **orchestrator.py** - The Conductor
- Coordinates all modules in correct sequence
- Manages daily workflow execution
- Handles error propagation to self-healer
- Generates final quality reports

### 2. **scout.py** - The Researcher
- Queries GitHub API with multiple strategies:
  - Trending repos (daily/weekly)
  - Topic-based discovery (ML, Python, JS, etc.)
  - "Old but gold" repos (high quality, maintained)
- Scores and ranks repositories
- Fetches README content for analysis

### 3. **scriptwriter.py** - The Writer
- Uses Groq LLM (llama-3.1-70b-versatile)
- Generates 60-90 second viral scripts
- Optimized hooks for first 3 seconds
- Platform-specific variations
- SEO-friendly metadata generation

### 4. **voice_generator.py** - The Narrator
- Microsoft Edge TTS (completely free)
- Professional neural voices
- Script cleaning and formatting
- Audio duration calculation
- Speed adjustment capabilities

### 5. **video_producer.py** - The Director
- Playwright browser automation
- Smooth GitHub page scrolling
- Screenshot capture at key points
- FFmpeg video encoding
- Audio/video synchronization
- Vertical format (1080x1920)

### 6. **distributor.py** - The Publisher
- YouTube Shorts via official API
- Instagram Reels via Zerino API
- Facebook Reels via Zerino API
- Platform-optimized captions
- Auto-generated hashtags and tags

### 7. **self_healer.py** - The Fixer
- AI-powered error analysis
- Pattern recognition for common issues
- Automatic fix generation
- Retry logic with intelligent delays
- Resource cleanup on failures
- Health reporting

## Data Flow

```
GitHub API → Scout → Repo Data
                        ↓
Repo Data → ScriptWriter → Script
                              ↓
Script → VoiceGenerator → Audio File
                                ↓
Repo URL + Audio → VideoProducer → Video File
                                          ↓
Video File → Distributor → [YouTube, Instagram, Facebook]
                                ↓
                         Self-Healer (monitors all steps)
```

## Key Features by Module

| Module | Key Feature | Technology |
|--------|-------------|------------|
| Scout | Multi-strategy discovery | GitHub API |
| ScriptWriter | Viral hook generation | Groq LLM |
| VoiceGenerator | Free professional TTS | Edge TTS |
| VideoProducer | Smooth browser navigation | Playwright + FFmpeg |
| Distributor | Multi-platform upload | YouTube API + Zerino |
| Self-Healer | AI error correction | Groq LLM |

## Execution Time Estimates

| Step | Duration | Notes |
|------|----------|-------|
| Scout repos | 30-60s | Depends on API rate limits |
| Generate script | 5-10s | Groq is very fast |
| Create voiceover | 10-20s | Edge TTS speed |
| Record video | 60-90s | Browser automation |
| Encode video | 30-60s | FFmpeg processing |
| Upload (all platforms) | 120-180s | Network dependent |
| **Total per video** | **~4-6 min** | |
| **Daily (3 videos)** | **~12-18 min** | Well within GitHub Actions limit |

## Customization Points

Each module can be customized:

1. **Scout**: Add new topics, change scoring algorithm
2. **ScriptWriter**: Modify prompts, adjust tone/style
3. **VoiceGenerator**: Change voice, adjust speed/pitch
4. **VideoProducer**: Change resolution, scroll patterns
5. **Distributor**: Customize captions, add branding
6. **Self-Healer**: Add new fix patterns, adjust retry logic

## Error Handling Strategy

```
Error Occurs
     ↓
Self-Healer analyzes
     ↓
┌────────────────────┐
│ Fix Type Decision  │
└────────────────────┘
     ↓
┌─────────┬──────────┬────────┬──────────┐
│  Retry  │  Skip    │ Cleanup│ Alternative│
└─────────┴──────────┴────────┴──────────┘
     ↓
Log & Continue or Escalate
```

## Security Notes

- All secrets stored in GitHub Secrets (never in code)
- API keys never logged or exposed
- Temporary files auto-cleaned after processing
- No sensitive data in artifacts
- Read-only GitHub token permissions (except workflow trigger)

## Performance Optimization

- Parallel processing where possible
- Efficient API usage with caching
- Minimal file I/O operations
- Streaming uploads for large videos
- Smart retry with exponential backoff

---

This architecture ensures reliable, autonomous operation with minimal maintenance while producing high-quality viral content daily!
