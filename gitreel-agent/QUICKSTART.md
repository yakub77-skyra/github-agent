# GitReel AI Agent - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Fork & Clone
```bash
# Fork this repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/gitreel-agent.git
cd gitreel-agent
```

### Step 2: Get Your API Keys (All Free!)

#### 1. Groq API Key (for LLM)
1. Go to https://console.groq.com/keys
2. Sign up / Log in
3. Click "Create API Key"
4. Copy the key

#### 2. YouTube API Key
1. Go to https://console.cloud.google.com/
2. Create a new project
3. Enable "YouTube Data API v3"
4. Go to Credentials → Create Credentials → API Key
5. Copy the key

#### 3. Zerino API Key (for Instagram & Facebook)
1. Go to https://zern.io/
2. Sign up for free account
3. Navigate to API section
4. Generate your API key
5. Copy the key

#### 4. GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo`, `workflow`
4. Generate and copy the token

### Step 3: Configure GitHub Secrets

1. Go to your forked repository on GitHub
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret** (add each one):

| Secret Name | Value |
|-------------|-------|
| `GROQ_API_KEY` | Your Groq API key |
| `YOUTUBE_API_KEY` | Your YouTube API key |
| `ZERNIO_API_KEY` | Your Zerino API key |
| `GITHUB_TOKEN` | Your GitHub token |

### Step 4: Enable Actions

1. Go to **Actions** tab
2. If you see "I understand my workflows, go ahead and enable them", click it
3. Your workflow is now active!

### Step 5: Test Run (Optional)

To test immediately without waiting for scheduled run:

1. Go to **Actions** tab
2. Click **"GitReel AI Agent - Daily Video Generation"**
3. Click **"Run workflow"** button
4. Select your branch (main/master)
5. Click **"Run workflow"**

### Step 6: Get Your Videos

After workflow completes (~10-20 minutes):

1. Stay in **Actions** tab
2. Click on the completed workflow run (green checkmark)
3. Scroll down to **Artifacts** section
4. Click **`gitreel-videos-{number}`** to download
5. Extract the ZIP file
6. Upload to YouTube Shorts, Instagram Reels, Facebook Reels!

## 📊 What You Get

Each day, the agent will create:
- ✅ 1-3 vertical videos (1080x1920)
- ✅ Professional voiceover narration
- ✅ Smooth GitHub page navigation
- ✅ Optimized titles and descriptions
- ✅ Platform-specific captions and hashtags

## ⏰ Schedule

- **Automatic**: Runs daily at 8:00 AM UTC
- **Manual**: Trigger anytime via Actions tab

## 💰 Cost

**$0.00** - Everything runs on free tiers!

- Groq: Free tier (1000+ requests/day)
- Edge TTS: Completely free
- GitHub Actions: Unlimited for public repos
- YouTube API: Free quota (10k units/day)
- Zerino: Free tier available

## 🔧 Troubleshooting

### Workflow doesn't start?
- Make sure Actions are enabled
- Check all 4 secrets are configured correctly
- Verify token has correct permissions

### Video generation fails?
- Download logs artifact to see detailed errors
- Common issues: invalid repo URLs, API rate limits
- Self-healer will retry automatically

### Can't download videos?
- Wait for workflow to complete fully (green checkmark)
- Artifacts are available for 7 days
- Try different browser if download fails

## 📱 Next Steps

1. **Customize**: Edit settings in `src/orchestrator.py`
2. **Brand**: Add your logo/watermark in post-processing
3. **Schedule**: Change cron time in workflow file
4. **Scale**: Increase `daily_repo_limit` if needed

## 🎯 Pro Tips

- Run manually first to test everything works
- Review first few videos before automating completely
- Monitor logs regularly for optimization opportunities
- Engage with comments on your posted videos
- Track which repos perform best for your audience

## 🆘 Need Help?

1. Check the full README.md for detailed documentation
2. Review logs in the artifacts
3. Open an issue on GitHub
4. Check Groq/API provider status pages

---

**Ready to create viral GitHub review videos?** 🚀

Your first video will be ready in about 15 minutes after the workflow starts!
