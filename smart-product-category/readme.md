# Smart Product Category API

An AI-powered REST API that automatically categorizes Woolworths products using Google's Gemini-Pro model.

## Features

- Fetches product details from Woolworths API
- Categorizes products using Google's Gemini AI
- Returns product type and varieties in JSON format
- Built with FastAPI for high performance
- Async operations for better scalability

## Prerequisites

- Python 3.8+
- Google Cloud API key for Gemini AI
- Poetry (Python package manager)
- Internet access for Woolworths API

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd smart-product-category
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Create a `.env` file in the project root:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

1. Start the server:
```bash
poetry run python -m app.main
```

2. The API will be available at `http://localhost:8000`

3. Make a request to categorize a product:
```bash
curl -X POST "http://localhost:8000/categorize" \
     -H "Content-Type: application/json" \
     -d '{"product_id": "123456"}'
```

## API Endpoints

### POST /categorize
Categorizes a Woolworths product by its ID.

Request body:
```json
{
    "product_id": "string"
}
```

Response:
```json
{
    "type": "string",
    "variety": ["string"]
}
```

### GET /health
Health check endpoint.

Response:
```json
{
    "status": "healthy"
}
```

## Project Structure

```
app/
├── __init__.py
├── main.py              # FastAPI application entry point
├── woolworths_client.py # Woolworths API client
├── gemini_client.py     # Google Gemini AI client
├── prompt_loader.py     # Prompt template loader
├── templates.py         # Response templates
├── schema.py           # Data models
├── config.py           # Configuration settings
└── api_models.py       # API request/response models
```

## Error Handling

The API includes comprehensive error handling for:
- Invalid product IDs
- Woolworths API failures
- AI model errors
- Invalid JSON responses

## License

[Your chosen license]