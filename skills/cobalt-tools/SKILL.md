---
name: cobalt-tools
description: Download videos, audio, and media from YouTube, TikTok, Twitter, Instagram, and 50+ platforms using Cobalt API or self-hosted instance. Use when user wants to download media, save videos, extract audio, or needs help with Cobalt tools API integration.
---

# Cobalt Tools

Open-source media downloader that works as a proxy - paste a link, get the file. No ads, no trackers, no caching.

## What Cobalt Does

- Downloads video (up to 8K), audio, GIFs from 50+ platforms
- Converts formats: mp3, ogg, wav, opus for audio
- No caching - works like a proxy, streams directly
- Supports: YouTube, TikTok, Twitter/X, Instagram, Reddit, Twitch, Vimeo, and more

## API Usage

### Self-Hosted Instance (Recommended)

The public API (`api.cobalt.tools`) has bot protection. For automated use, **host your own instance**.

```bash
# Docker run
docker run -d --name cobalt -p 9000:9000 ghcr.io/imputnet/cobalt:latest

# Or docker-compose
# See: https://github.com/imputnet/cobalt/blob/main/docs/run-an-instance.md
```

### API Endpoint

**POST** `/` with JSON body:

```json
{
  "url": "https://youtube.com/watch?v=...",
  "videoQuality": "1080",
  "audioFormat": "mp3",
  "audioBitrate": "128"
}
```

**Headers required:**
```
Accept: application/json
Content-Type: application/json
Authorization: Api-Key <key>  // if instance requires auth
```

### Request Parameters

| Key | Values | Default |
|-----|--------|---------|
| url | (required) | - |
| videoQuality | max/4320/2160/1440/1080/720/480/360/240/144 | 1080 |
| audioFormat | best/mp3/ogg/wav/opus | mp3 |
| audioBitrate | 320/256/128/96/64/8 | 128 |
| downloadMode | auto/audio/mute | auto |
| filenameStyle | classic/pretty/basic/nerdy | basic |
| disableMetadata | true/false | false |
| alwaysProxy | true/false | false |

### YouTube-Specific Options

| Key | Values | Default |
|-----|--------|---------|
| youtubeVideoCodec | h264/av1/vp9 | h264 |
| youtubeVideoContainer | auto/mp4/webm/mkv | auto |
| youtubeDubLang | ISO 639-1 code | none |
| youtubeBetterAudio | true/false | false |
| youtubeHLS | true/false | false |

### Response Types

| Status | Meaning |
|--------|---------|
| tunnel | Cobalt is proxying/remuxing the file |
| redirect | Direct link to service URL |
| picker | Multiple items to choose from |
| error | Error with code in `error.code` |

### Example: Download Audio

```bash
curl -X POST https://your-cobalt-instance/ \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://youtube.com/watch?v=dQw4w9WgXcQ", "downloadMode": "audio", "audioFormat": "mp3"}'
```

### Example: Get Video Info First

```bash
# GET / returns instance info
curl https://your-cobalt-instance/
```

## Common Error Codes

- `api.link.invalid` - URL not recognized
- `api.fetch.fail` - Could not fetch from source
- `api.content.unavailable` - Content not available
- `api.rate_exceeded` - Rate limit hit
- `api.auth.api_key.missing` - API key required

## Quick Download Function

Use the bundled script to download media:

```bash
# Download video (default 1080p)
node scripts/cobalt-download.js --url "https://youtube.com/watch?v=..." --api "http://localhost:9000"

# Download audio only
node scripts/cobalt-download.js --url "https://youtube.com/watch?v=..." --mode audio --format mp3

# Get instance info
node scripts/cobalt-download.js --info

# Raw JSON output
node scripts/cobalt-download.js --url "https://..." --json
```

### Environment Variables

- `COBALT_API_URL` - Default API endpoint
- `COBALT_API_KEY` - API key if instance requires auth

## Self-Hosting Options

1. **Docker**: `ghcr.io/imputnet/cobalt:latest`
2. **Railway**: One-click deploy template available
3. **Manual**: Clone and build from source

See: https://github.com/imputnet/cobalt/blob/main/docs/run-an-instance.md

## Notes

- Cobalt never caches - it's a proxy
- Only downloads publicly accessible content
- Not a piracy tool - same as browser dev tools
- AGPL-3.0 licensed