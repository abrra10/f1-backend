# FormulaHub API Backend

A FastAPI backend for FormulaHub that provides Formula 1 data through RESTful API endpoints. Supports both local development and Cloudflare Workers deployment.

## 🚀 Features

- **FastAPI Integration**: Modern, fast web framework with automatic API documentation
- **FastF1 Integration**: Rich F1 data including lap times, telemetry, session data, weather
- **Cloudflare Workers Support**: Serverless deployment with Python runtime
- **Caching**: Redis-based caching with in-memory fallback
- **CORS Support**: Configured for frontend integration
- **Real-time Countdown**: Dynamic race countdown calculations
- **Multiple Data Sources**: Ergast API fallback for Cloudflare Workers

## 📋 Prerequisites

- Python 3.8+
- Node.js (for Cloudflare Workers deployment)
- Cloudflare account (for deployment)

## 🛠️ Installation

### Local Development

1. **Clone the repository**

   ```bash
   git clone <your-backend-repo-url>
   cd formulahub-backend
   ```

2. **Create virtual environment**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### Cloudflare Workers Deployment

1. **Install Wrangler CLI**

   ```bash
   npm install -g wrangler
   ```

2. **Login to Cloudflare**

   ```bash
   wrangler login
   ```

3. **Deploy**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

## 📚 API Endpoints

### Health Check

- `GET /api/health` - Health check endpoint

### Drivers

- `GET /api/drivers` - Get all drivers for current season
- `GET /api/drivers/{driver_id}` - Get specific driver information

### Standings

- `GET /api/standings` - Get current driver standings
- `GET /api/standings/driver/{driver_id}` - Get specific driver's standing

### Races

- `GET /api/races` - Get all races for current season
- `GET /api/races/next` - Get next upcoming race with countdown
- `GET /api/races/{race_id}` - Get specific race information
- `GET /api/races/{race_id}/results` - Get race results

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true
LOG_LEVEL=info

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600

# FastF1 Configuration
CURRENT_SEASON=2025
FASTF1_CACHE_DIR=./cache
FASTF1_VERBOSE=false

# CORS Configuration
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","https://formulahub.vercel.app"]
```

### Cloudflare Workers Configuration

The `wrangler.toml` file contains the Cloudflare Workers configuration:

```toml
name = "formulahub-api"
main = "worker.py"
compatibility_date = "2024-01-15"
compatibility_flags = ["python"]
```

## 🏃‍♂️ Running the Application

### Development Mode

```bash
python main.py
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Cloudflare Workers

```bash
wrangler deploy --env production
```

## 📊 Data Sources

### Local Development

- **Primary**: FastF1 library with comprehensive F1 data
- **Cache**: Redis (optional) with in-memory fallback
- **Features**: Lap times, telemetry, session data, weather

### Cloudflare Workers

- **Primary**: Ergast API (https://ergast.com/api/f1/)
- **Cache**: In-memory cache with 30-minute TTL
- **Features**: Basic F1 data with real-time countdown

## 🔄 Deployment

### Local Development

The application runs on `http://localhost:8000` with automatic reloading.

### Cloudflare Workers

Deploy to Cloudflare Workers for free hosting:

```bash
# Quick deployment
./deploy.sh

# Manual deployment
wrangler deploy --env production
```

Your API will be available at: `https://formulahub-api.your-subdomain.workers.dev`

## 📝 API Documentation

### Local Development

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Cloudflare Workers

API documentation is available at the root endpoint with available routes.

## 🧪 Testing

```bash
# Run tests
python -m pytest

# Test API endpoints
python test_api.py
```

## 📁 Project Structure

```
f1-backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── drivers.py
│   │       ├── standings.py
│   │       ├── races.py
│   │       └── health.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── schemas.py
│   └── services/
│       ├── fastf1_service.py
│       └── cache_service.py
├── cache/                 # FastF1 cache directory
├── main.py               # FastAPI application entry point
├── worker.py             # Cloudflare Workers entry point
├── wrangler.toml         # Cloudflare Workers configuration
├── requirements.txt      # Python dependencies
├── requirements-cloudflare.txt  # Minimal dependencies for Cloudflare
├── deploy.sh             # Deployment script
└── README.md
```

## 🔍 Monitoring

### Local Development

- Logs are printed to console
- Use `uvicorn` with `--log-level debug` for detailed logs

### Cloudflare Workers

```bash
# View real-time logs
wrangler tail

# Check deployment status
wrangler whoami
```

## 🚨 Troubleshooting

### Common Issues

1. **Import errors**

   - Ensure virtual environment is activated
   - Install all dependencies: `pip install -r requirements.txt`

2. **CORS errors**

   - Check CORS configuration in `app/core/config.py`
   - Verify frontend domain is in allowed origins

3. **FastF1 cache issues**

   - Clear cache directory: `rm -rf cache/`
   - Check internet connection for data download

4. **Cloudflare deployment fails**
   - Verify Wrangler CLI installation: `wrangler --version`
   - Check Cloudflare login: `wrangler whoami`
   - Review `wrangler.toml` configuration

### Performance Tips

- Use Redis for caching in production
- Configure appropriate cache TTL values
- Monitor API response times
- Use Cloudflare Workers for global distribution

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [FastF1 Documentation](https://docs.fastf1.dev/)
- [Cloudflare Workers Documentation](https://developers.cloudflare.com/workers/)
- [Ergast API](https://ergast.com/mrd/)

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review the API documentation
3. Open an issue on GitHub
4. Check the deployment logs
