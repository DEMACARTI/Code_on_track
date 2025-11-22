# Code on Track - QR-Based Digital Identity System

A backend system for managing digital identities of Indian Railways track fittings using QR codes.

## Features

- Generate unique QR codes for railway track fittings
- Track lifecycle of components (manufactured → supplied → inspected → installed → performance → replaced)
- Store component details including vendor, lot number, and warranty information
- Secure file storage using MinIO (S3 compatible)
- RESTful API for integration with frontend applications

## Prerequisites

- Docker and Docker Compose
- Python 3.8+
- Git

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Code_on_track
   ```

2. **Set up environment variables**
   - Copy `.env.example` to `.env` and update the values if needed:
     ```bash
     cp .env.example .env
     ```

3. **Build and start the services**
   ```bash
   docker-compose up --build -d
   ```
   This will start:
   - FastAPI application on port 8000
   - PostgreSQL database on port 5432
   - MinIO (S3-compatible storage) on port 9000 (API) and 9001 (Console)
   - Redis on port 6379 (for future use)

4. **Access the services**
   - **API Documentation**: http://localhost:8000/api/docs
   - **MinIO Console**: http://localhost:9001 (username: minioadmin, password: minioadmin)
   - **Database**: PostgreSQL is available at localhost:5432

## API Endpoints

### Create Items
- **POST** `/api/items/` - Create one or more items with QR codes
  ```json
  {
    "component_type": "ERC",
    "lot_number": "LOT12345",
    "vendor_id": "VENDOR001",
    "warranty_years": 5,
    "manufacture_date": "2025-11-22",
    "quantity": 1
  }
  ```

### Get Item Details
- **GET** `/api/items/{uid}` - Get details of a specific item by UID

## Development

### Running Locally

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the development server:
   ```bash
   uvicorn App_a.app.main:app --reload
   ```

### Database Migrations

For database schema changes, you can use Alembic:

```bash
# Install Alembic
pip install alembic

# Create a new migration
alembic revision --autogenerate -m "Your migration message"

# Apply migrations
alembic upgrade head
```

## Project Structure

```
Code_on_track/
│
├── App_a/                     # Main application package
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application
│   │   ├── database.py       # Database configuration
│   │   ├── models.py         # SQLAlchemy models
│   │   ├── schemas.py        # Pydantic models
│   │   ├── minio_client.py   # MinIO client for file storage
│   │   └── qr_generator.py   # QR code generation
│   └── __init__.py
│
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                # Application Dockerfile
├── .env                      # Environment variables
└── requirements.txt          # Python dependencies
```

## Environment Variables

See `.env.example` for a list of required environment variables.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Team

- [Your Team Name] - SIH 2025
