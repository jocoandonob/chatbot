# Document Q&A Application

A Flask-based web application that allows users to upload documents or process URLs, and then ask questions about their content using AI-powered responses.

## Features

- Document Upload: Support for TXT and PDF files
- URL Processing: Extract and process content from web pages
- AI-Powered Q&A: Ask questions about uploaded content
- Request Limiting: Rate limiting to prevent abuse
- Visitor Counter: Track number of visitors
- Health Check Endpoint: Monitor application status

## Prerequisites

- Python 3.x
- Flask
- SQLAlchemy
- OpenAI API key (for AI-powered responses)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export SESSION_SECRET="your-secret-key"
export DATABASE_URL="your-database-url"
export OPENAI_API_KEY="your-openai-api-key"
```

## Running the Application

1. Start the Flask application:
```bash
python flask_app.py
```

2. Access the application at `http://localhost:5000`

## API Endpoints

- `GET /`: Main application page
- `GET /visitor-count`: Get current visitor count
- `POST /upload`: Upload a document (TXT or PDF)
- `POST /ask`: Ask a question about uploaded content
- `POST /process-url`: Process content from a URL
- `GET /remaining-requests`: Check remaining question quota
- `GET /health`: Health check endpoint

## Usage

1. Upload a document or process a URL
2. Wait for the content to be processed
3. Ask questions about the content
4. Receive AI-powered responses based on the document content

## Rate Limiting

The application implements a rate limit of 5 questions per user to prevent abuse.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 