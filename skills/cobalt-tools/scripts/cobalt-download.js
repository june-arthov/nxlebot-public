#!/usr/bin/env node
/**
 * Cobalt API Client - Download media from YouTube, TikTok, Twitter, Instagram, etc.
 * 
 * Usage:
 *   node cobalt-download.js --url "https://youtube.com/watch?v=..." [options]
 * 
 * Options:
 *   --url          Media URL (required)
 *   --api          Cobalt API URL (default: http://localhost:9000 or COBALT_API_URL env)
 *   --key          API key if required (or COBALT_API_KEY env)
 *   --mode         Download mode: auto, audio, mute (default: auto)
 *   --quality      Video quality: max/4320/2160/1440/1080/720/480/360/240/144 (default: 1080)
 *   --format       Audio format: mp3/ogg/wav/opus (default: mp3)
 *   --bitrate      Audio bitrate: 320/256/128/96/64/8 (default: 128)
 *   --output       Output filename (optional)
 *   --info         Get instance info instead of downloading
 *   --json         Output raw JSON response
 */

const fs = require('fs');
const https = require('https');
const http = require('http');

const args = process.argv.slice(2);
const flags = {};

for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].slice(2);
    if (args[i + 1] && !args[i + 1].startsWith('--')) {
      flags[key] = args[++i];
    } else {
      flags[key] = true;
    }
  }
}

const API_URL = flags.api || process.env.COBALT_API_URL || 'http://localhost:9000';
const API_KEY = flags.key || process.env.COBALT_API_KEY;

async function cobaltRequest(endpoint, body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(endpoint, API_URL);
    const protocol = url.protocol === 'https:' ? https : http;
    
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      method: body ? 'POST' : 'GET',
      headers: {
        'Accept': 'application/json',
      }
    };
    
    if (body) {
      options.headers['Content-Type'] = 'application/json';
    }
    
    if (API_KEY) {
      options.headers['Authorization'] = `Api-Key ${API_KEY}`;
    }
    
    const req = protocol.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve({ status: 'error', raw: data, statusCode: res.statusCode });
        }
      });
    });
    
    req.on('error', reject);
    
    if (body) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

async function downloadFile(url, outputPath) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https:') ? https : http;
    const file = fs.createWriteStream(outputPath);
    
    protocol.get(url, (response) => {
      if (response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
        downloadFile(response.headers.location, outputPath).then(resolve).catch(reject);
        return;
      }
      
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve(outputPath);
      });
    }).on('error', (err) => {
      fs.unlink(outputPath, () => reject(err));
    });
  });
}

async function main() {
  // Get instance info
  if (flags.info) {
    const info = await cobaltRequest('/');
    console.log(JSON.stringify(info, null, 2));
    return;
  }
  
  // Download
  if (!flags.url) {
    console.error('Error: --url is required');
    console.error('Usage: node cobalt-download.js --url "https://..." [--api URL] [--key KEY] [--mode auto|audio|mute] [--quality 1080] [--format mp3]');
    process.exit(1);
  }
  
  const requestBody = {
    url: flags.url,
  };
  
  if (flags.mode) requestBody.downloadMode = flags.mode;
  if (flags.quality) requestBody.videoQuality = flags.quality;
  if (flags.format) requestBody.audioFormat = flags.format;
  if (flags.bitrate) requestBody.audioBitrate = flags.bitrate;
  if (flags.mode === 'audio') requestBody.downloadMode = 'audio';
  
  console.error(`Requesting: ${flags.url}`);
  const response = await cobaltRequest('/', requestBody);
  
  if (flags.json) {
    console.log(JSON.stringify(response, null, 2));
    return;
  }
  
  if (response.status === 'error') {
    console.error(`Error: ${response.error?.code || 'Unknown error'}`);
    console.error(JSON.stringify(response.error, null, 2));
    process.exit(1);
  }
  
  if (response.status === 'tunnel' || response.status === 'redirect') {
    const filename = flags.output || response.filename || 'download';
    console.error(`Downloading: ${response.url}`);
    console.error(`Saving as: ${filename}`);
    
    await downloadFile(response.url, filename);
    console.log(`Downloaded: ${filename}`);
    return;
  }
  
  if (response.status === 'picker') {
    console.log('Multiple items available:');
    response.picker.forEach((item, i) => {
      console.log(`  [${i}] ${item.type}: ${item.url}`);
    });
    return;
  }
  
  if (response.status === 'local-processing') {
    console.log('Local processing required:');
    console.log(JSON.stringify(response, null, 2));
    return;
  }
  
  console.log(JSON.stringify(response, null, 2));
}

main().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});