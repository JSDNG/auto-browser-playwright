# Auto Flash Sale - HideMyAcc Automation

Automated Flash Sale system using HideMyAcc API for browser automation.

## 🚀 Features

- **HideMyAcc Integration**: Full API integration for profile management
- **RESTful API**: Clean REST API for external integrations
- **Profile Management**: Start/stop profiles with retry logic
- **Rate Limiting**: Built-in rate limiting and security
- **Docker Support**: Ready for containerized deployment
- **Monitoring**: Health checks and logging
- **Webhook Support**: Integration with external services (n8n, etc.)

## 📁 Project Structure

```
auto-fls/
├─ .env                    # Environment configuration
├─ requirements.txt        # Python dependencies
├─ app/
│  ├─ __init__.py         # Package initialization
│  ├─ config.py           # Configuration management
│  ├─ hma_client.py       # HideMyAcc API client
│  ├─ utils.py            # Utility functions
│  └─ routes.py           # API routes
├─ server.py              # Main Flask application
├─ docker/
│  ├─ Dockerfile          # Docker image definition
│  ├─ docker-compose.yml  # Docker Compose configuration
│  ├─ ngrok.yml          # Ngrok tunnel configuration
│  └─ prometheus.yml     # Monitoring configuration
└─ logs/                  # Application logs
```

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- HideMyAcc desktop application
- Docker (optional)

### Local Development

1. **Clone and setup**:
   ```bash
   cd auto-fls
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Start HideMyAcc**:
   - Launch HideMyAcc desktop app
   - Ensure API server is running (usually port 2268)

4. **Run the application**:
   ```bash
   python server.py
   ```

### Docker Deployment

1. **Build and run**:
   ```bash
   cd docker
   docker-compose up -d
   ```

2. **Check status**:
   ```bash
   docker-compose ps
   docker-compose logs -f auto-fls
   ```

## 📚 API Documentation

### Base URL
- Local: `http://localhost:5001/api/v1`
- Docker: `http://localhost:5001/api/v1`

### Endpoints

#### Health Check
```http
GET /api/v1/health
```

#### List Profiles
```http
GET /api/v1/profiles
```

#### Start Profile
```http
POST /api/v1/profiles/{profile_id}/start
Content-Type: application/json

{
  "open_tabs": ["https://example.com"]
}
```

#### Stop Profile
```http
POST /api/v1/profiles/{profile_id}/stop
```

#### Get Profile Status
```http
GET /api/v1/profiles/{profile_id}/status
```

#### Get Active Profiles
```http
GET /api/v1/profiles/active
```

### Example Usage

```python
import requests

# Start a profile
response = requests.post(
    "http://localhost:5001/api/v1/profiles/6898c8f7effa52a76ed48168/start",
    json={"open_tabs": ["https://seller.tiktok.com"]}
)

if response.status_code == 200:
    data = response.json()
    print(f"Profile started on port: {data['data']['port']}")
    print(f"WebSocket URL: {data['data']['ws_url']}")
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HMA_API_BASE` | HideMyAcc API base URL | `http://127.0.0.1:2268` |
| `HMA_API_KEY` | HideMyAcc API key | - |
| `SERVER_HOST` | Server host | `0.0.0.0` |
| `SERVER_PORT` | Server port | `5001` |
| `DEBUG` | Debug mode | `False` |
| `LOG_LEVEL` | Logging level | `INFO` |

### HideMyAcc Setup

1. **Install HideMyAcc**: Download from official website
2. **Create profiles**: Set up your browser profiles
3. **Enable API**: Ensure API server is running
4. **Get profile IDs**: Use the list profiles endpoint

## 🐳 Docker Configuration

### Docker Compose Services

- **auto-fls**: Main application server
- **ngrok**: Public tunnel (optional)
- **prometheus**: Monitoring (optional)

### Customization

Edit `docker/docker-compose.yml` to:
- Change ports
- Add environment variables
- Configure volumes
- Enable/disable services

## 📊 Monitoring

### Health Checks

- Application: `GET /api/v1/health`
- Docker: Built-in health checks
- Prometheus: Metrics endpoint (if enabled)

### Logs

- Application logs: `logs/auto_fls.log`
- Docker logs: `docker-compose logs -f auto-fls`

## 🔒 Security

- Rate limiting on all endpoints
- Input validation for profile IDs
- Error handling and logging
- CORS configuration
- Environment-based secrets

## 🚨 Troubleshooting

### Common Issues

1. **Connection refused to HMA**:
   - Check if HideMyAcc is running
   - Verify port 2268 is accessible
   - Check firewall settings

2. **License errors (402)**:
   - Renew HideMyAcc license
   - Check billing status

3. **Profile not found (400)**:
   - Verify profile ID exists
   - Check profile is not already running

### Debug Mode

Enable debug mode:
```bash
export DEBUG=True
python server.py
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review logs for error details
- Open an issue on GitHub
