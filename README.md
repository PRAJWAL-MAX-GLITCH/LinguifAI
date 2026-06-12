<div align="center">
  <img src="./frontend/public/globe.svg" alt="LinguifAI Logo" width="100" />
  <h1>🌍 LinguifAI</h1>
  <p><strong>Next-Generation AI-Powered Language Translation Platform</strong></p>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
  [![Status](https://img.shields.io/badge/status-active-success.svg)]()
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![Next.js](https://img.shields.io/badge/Next.js-black?style=flat&logo=next.js)](https://nextjs.org/)
</div>

<br />

LinguifAI is a powerful, modern, and scalable language translation application designed to bridge communication gaps seamlessly. Leveraging state-of-the-art Large Language Models (LLMs), it offers real-time text and document translations with unmatched context-awareness and accuracy.

## ✨ Key Features
- **Intelligent Translation**: Context-aware translations powered by multiple AI providers (OpenAI, Google Gemini, Groq, DeepSeek).
- **Document Processing**: Upload and translate entire documents (`.pdf`, `.docx`) natively without losing formatting context.
- **Real-time Performance**: Lightning-fast translation powered by asynchronous task queues and Redis caching.
- **Secure Authentication**: Robust user session management with NextAuth and JWTs.
- **Beautiful UI**: A highly responsive, modern interface built with Next.js, TailwindCSS v4, and Shadcn UI.

---

## 🛠️ Technology Stack & Tools

### Frontend
- **Framework**: [Next.js (v16)](https://nextjs.org/) with React 19
- **Styling**: [TailwindCSS v4](https://tailwindcss.com/) & [Shadcn UI](https://ui.shadcn.com/)
- **State Management**: [Zustand](https://zustand-demo.pmnd.rs/) & [React Query](https://tanstack.com/query)
- **Authentication**: [NextAuth.js](https://next-auth.js.org/)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+)
- **Database (ORM)**: [PostgreSQL](https://www.postgresql.org/) with [SQLAlchemy (asyncio)](https://www.sqlalchemy.org/) & [Alembic](https://alembic.sqlalchemy.org/) for migrations
- **Task Queue & Caching**: [Celery](https://docs.celeryq.dev/) + [Redis](https://redis.io/)
- **Security**: Passlib (Bcrypt) & Python-JOSE

### AI Integration
- Integrations with **OpenAI**, **Google Generative AI (Gemini)**, **Groq**, and **DeepSeek** via dedicated provider interfaces.
- **Document Parsers**: `pdfplumber` & `python-docx` for rich text extraction.

### DevOps & Tools
- **Docker & Docker Compose**: Fully containerized environment for consistent local setup.
- **Git**: Version control system used for feature branching and CI/CD pipelines.

---

## ⚙️ How It Works

1. **User Interaction**: Users interact with the sleek Next.js frontend, typing text or uploading documents.
2. **API Layer**: The Next.js frontend securely communicates with the Python FastAPI backend via authenticated asynchronous HTTP requests.
3. **Task Delegation**:
   - For **instant text translation**, the request is routed immediately to the selected AI Provider API (e.g., Gemini, OpenAI).
   - For **large documents**, the FastAPI backend enqueues the extraction and translation job using **Celery & Redis**, ensuring the main thread remains unblocked and responsive.
4. **Data Persistence**: Translated text, document histories, and usage logs are safely stored in the **PostgreSQL** database.
5. **Real-time Delivery**: Results are efficiently served back to the React UI, utilizing caching techniques for repeated translations to minimize latency.

---

## 🚀 Quick Start

### Prerequisites
- [Docker](https://www.docker.com/) and Docker Compose installed.

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/PRAJWAL-MAX-GLITCH/LinguifAI.git
   cd LinguifAI
   ```

2. **Configure Environment Variables**
   - Copy `backend/.env.example` to `backend/.env` and insert your API keys (OpenAI, Gemini, Groq, etc).

3. **Start the application**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - **Frontend Interface**: `http://localhost:3000`
   - **Backend API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📜 License
This project is [MIT](https://opensource.org/licenses/MIT) licensed.
