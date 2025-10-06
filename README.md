# Google Sheets Bot

A Telegram bot for managing Google Sheets transactions with Redis caching.

## Features

- Telegram bot interface using aiogram
- Google Sheets integration
- Redis caching for keyboard data
- Docker containerization
- CI/CD with GitHub Actions

## Development

### Prerequisites

- Python 3.13+
- uv package manager
- Docker and Docker Compose
- Redis server

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd googlesheetsbot
```

2. Install dependencies:
```bash
uv sync
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run with Docker Compose:
```bash
docker-compose up -d
```

5. Or run locally:
```bash
uv run python googlesheetsbot/app.py
```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Google OAuth
CLIENT_ID=your_google_client_id
CLIENT_SECRET=your_google_client_secret
SERVICE_ACCOUNT_FILE=path/to/service-account.json

# Google Sheets
SHEET_NAME=your_sheet_name
TRANSACTIONS_COLUMN=7
INCOME_COLUMN=1

# Telegram Bot
BOT_TOKEN=your_bot_token
USER_ID=your_telegram_user_id

# Redis
REDIS_DSN=redis://localhost:6379/0
KEYBOARD_KEY=keyboard

# Server
SERVER__HOST=0.0.0.0
SERVER__PORT=8000

# Webhook
SECRET_TOKEN=your_webhook_secret
WEBHOOK_PATH=/webhook
BASE_WEBHOOK_URL=https://yourdomain.com
```

## Docker

### Build and Run

```bash
# Build the image
docker build -t googlesheetsbot .

# Run the container
docker run -p 8000:8000 --env-file .env googlesheetsbot
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## CI/CD

This project includes comprehensive CI/CD pipelines using GitHub Actions:

### Continuous Integration (CI)

The CI pipeline runs on every push and pull request:

- **Code Quality**: Linting with ruff, formatting checks
- **Testing**: Unit tests (when available)
- **Type Checking**: MyPy type checking
- **Docker Build**: Builds and tests Docker image

### Continuous Deployment (CD)

The CD pipeline runs on pushes to main branch:

- **Docker Registry**: Builds and pushes to GitHub Container Registry
- **Multi-arch Support**: Supports multiple architectures
- **Deployment**: Ready for deployment to various platforms

### Security Scanning

Weekly security scans include:

- **Dependency Scanning**: Safety checks for known vulnerabilities
- **Code Analysis**: Bandit security linter
- **Container Scanning**: Trivy vulnerability scanner
- **GitHub Security**: Results uploaded to GitHub Security tab

## Workflows

- `ci.yml`: Continuous Integration
- `cd.yml`: Continuous Deployment  
- `security.yml`: Security scanning

## Deployment

The CD pipeline is configured to deploy to GitHub Container Registry. To deploy to other platforms:

1. **AWS ECS/Fargate**: Uncomment and configure AWS deployment steps
2. **Google Cloud Run**: Add Google Cloud deployment steps
3. **Azure Container Instances**: Add Azure deployment steps
4. **Kubernetes**: Add kubectl deployment steps
5. **Custom Server**: Use the SSH deployment example

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting: `uv run ruff check . && uv run ruff format .`
5. Submit a pull request

## License

[Add your license here]
