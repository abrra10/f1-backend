# FormulaHub API - Cloudflare Workers Deployment Guide

This guide will help you deploy the FormulaHub API to Cloudflare Workers for free hosting.

## Prerequisites

1. **Cloudflare Account**: Sign up at [cloudflare.com](https://cloudflare.com)
2. **Node.js**: Install Node.js (for Wrangler CLI)
3. **Wrangler CLI**: Install the Cloudflare Workers CLI

## Installation Steps

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
```

### 2. Login to Cloudflare

```bash
wrangler login
```

This will open your browser to authenticate with Cloudflare.

### 3. Configure Your Project

The project is already configured with:

- `wrangler.toml` - Cloudflare Workers configuration
- `worker.py` - Main worker code
- `requirements-cloudflare.txt` - Python dependencies

## Deployment Options

### Option 1: Quick Deploy (Recommended)

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment script
./deploy.sh
```

### Option 2: Manual Deploy

```bash
# Deploy to staging first
wrangler deploy --env staging

# If successful, deploy to production
wrangler deploy --env production
```

### Option 3: Deploy to Custom Domain (Optional)

1. Add your domain to Cloudflare
2. Uncomment the routes section in `wrangler.toml`
3. Update the domain name
4. Deploy with custom domain

## API Endpoints

Once deployed, your API will be available at:

- **Root**: `https://formulahub-api.your-subdomain.workers.dev/`
- **Health Check**: `https://formulahub-api.your-subdomain.workers.dev/api/health`
- **Drivers**: `https://formulahub-api.your-subdomain.workers.dev/api/drivers`
- **Standings**: `https://formulahub-api.your-subdomain.workers.dev/api/standings`
- **Races**: `https://formulahub-api.your-subdomain.workers.dev/api/races`
- **Next Race**: `https://formulahub-api.your-subdomain.workers.dev/api/races/next`

## Update Frontend Configuration

After deployment, update your frontend API configuration:

```javascript
// src/config/api.js
const API_BASE_URL = "https://formulahub-api.your-subdomain.workers.dev";

export const API_ENDPOINTS = {
  DRIVERS: `${API_BASE_URL}/api/drivers`,
  STANDINGS: `${API_BASE_URL}/api/standings`,
  RACES: `${API_BASE_URL}/api/races`,
  NEXT_RACE: `${API_BASE_URL}/api/races/next`,
  HEALTH: `${API_BASE_URL}/api/health`,
};
```

## Features

### ✅ What Works

- All API endpoints (drivers, standings, races, next race)
- CORS support for frontend integration
- In-memory caching (30-minute TTL)
- Real-time countdown calculation
- Health check endpoint
- Error handling

### ⚠️ Limitations

- No persistent storage (cache resets on cold starts)
- Limited to Cloudflare Workers runtime
- No FastF1 integration (uses Ergast API as fallback)
- 30-second execution time limit

### 🔄 Data Sources

- **Primary**: Ergast API (https://ergast.com/api/f1/)
- **Caching**: In-memory cache with 30-minute TTL
- **Fallback**: Error responses with helpful messages

## Monitoring

### View Logs

```bash
wrangler tail
```

### Check Status

```bash
wrangler whoami
```

### Update Deployment

```bash
wrangler deploy --env production
```

## Troubleshooting

### Common Issues

1. **"Wrangler not found"**

   ```bash
   npm install -g wrangler
   ```

2. **"Not logged in"**

   ```bash
   wrangler login
   ```

3. **"Deployment failed"**

   - Check your internet connection
   - Verify Cloudflare account status
   - Check wrangler.toml configuration

4. **"CORS errors"**
   - Verify the CORS headers in worker.py
   - Check your frontend domain is allowed

### Performance Tips

- The API uses caching to reduce external API calls
- Cache expires after 30 minutes
- Cold starts may take a few seconds
- Consider using a custom domain for better performance

## Cost

- **Free Tier**: 100,000 requests/day
- **Paid Plans**: Available if you exceed free limits
- **Custom Domains**: Free with Cloudflare

## Support

If you encounter issues:

1. Check the Cloudflare Workers documentation
2. Review the worker.py code for errors
3. Test endpoints individually
4. Check the deployment logs with `wrangler tail`
