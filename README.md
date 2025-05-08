# Educational AI Chatbot

An innovative AI-powered educational chatbot that provides accurate, curriculum-aligned responses based on 6th-grade textbook content. Built with Next.js, OpenAI, and Supabase Vector database, this tool ensures students receive reliable answers strictly from authorized educational materials.

## Features

- **Curriculum-Aligned Responses**: All answers are sourced exclusively from 6th-grade textbooks
- **Vector Database Integration**: Efficient semantic search using Supabase Vector
- **AI-Powered Q&A**: Advanced language model integration with OpenAI
- **Modern Web Interface**: Built with Next.js for optimal user experience
- **Content Verification**: Ensures responses are strictly based on authorized educational content
- **Scalable Architecture**: Designed for handling multiple concurrent users

## Tech Stack

- **Frontend**: Next.js
- **AI Integration**: OpenAI API
- **Vector Database**: Supabase Vector
- **Authentication**: Supabase Auth
- **Deployment**: Vercel (recommended)

## Prerequisites

- Node.js 18.x or higher
- OpenAI API key
- Supabase account and project
- 6th-grade textbook content (PDF format)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
```

Required environment variables:
```env
NEXT_PUBLIC_SUPABASE_URL=your-supabase-url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
OPENAI_API_KEY=your-openai-api-key
```

4. Initialize the vector database:
```bash
npm run init-db
```

## Usage

1. Start the development server:
```bash
npm run dev
```

2. Access the application at `http://localhost:3000`

## Vector Database Setup

1. Process textbook content:
```bash
npm run process-content
```

2. Generate embeddings:
```bash
npm run generate-embeddings
```

## Project Structure

```
├── app/                 # Next.js app directory
├── components/         # React components
├── lib/               # Utility functions
├── public/            # Static assets
├── styles/            # CSS styles
└── vector-db/         # Vector database scripts
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the language model capabilities
- Supabase for vector database infrastructure
- Next.js team for the amazing framework 