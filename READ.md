# 📘 OpenQQuantify AI Plugin – README

Welcome to the OpenQQuantify AI Plugin – an AI-powered multi-agent system designed to perform complex tasks such as tutoring assistance, resume building, startup advisory, and personalized product recommendations.

Built with Flask, this plugin can be integrated directly with ChatGPT using OpenAI’s plugin framework.

 Features
AI-Powered Electronic Recommendation Engine On-Demand Tutoring Agent (Subject Explanations)
Resume Generator & Optimization Agent
Startup Roadmap Assistant
Multi-Agent Delegation via Internal API Calls
GPT-4o-mini Powered Product Summarization & Comparison
Plugin-ready Manifest for ChatGPT (`ai-plugin.json`)
Optionally supports Voice/Chat UI frontend
Deployable to Render, Replit, Vercel, HuggingFace, etc.

Project Structure

├── main.py                 # Flask app with core logic + GPT-4o-mini integration
├── auth.py                 # Authentication blueprint (register, login, email verification, password reset)
├── models.py               # Database models (User, AIAgent)
├── emails_utils.py         # Utility for sending emails
├── agents/                 # Directory for specialized AI agents (Empty placeholders or actual agent files)
│   ├── tutoring_agent.py   # Explains complex topics
│   ├── resume_agent.py     # Builds/updates resumes
│   └── startup_agent.py    # Provides startup advice
├── products.json           # Sample product catalog used for recommendations
├── ai-plugin.json          # Primary Plugin manifest (for ChatGPT, details plugin metadata)
├── openapi.yaml            # API documentation (OpenAPI spec for plugin endpoints)
├── templates/              # HTML templates for rendering web pages (e.g., index.html)
├── static/                 # Static files (e.g., plugin logo)
│   └── logo.png            # Plugin logo image
└── .well-known/            # Required directory for ChatGPT plugin discovery
    └── ai-plugin.json      # This file *must* be accessible for ChatGPT plugin setup


 Running Locally
1.  Clone the Repo
    ```bash
    git clone [https://github.com/openqquantify/ai-plugin.git](https://github.com/openqquantify/ai-plugin.git)
    cd ai-plugin
    ```
2.  Install Dependencies
    ```bash
    pip install -r requirements.txt
    ```
3.  Set Environment Variables
    Create a `.env` file in the root directory (based on `.env.example`) and fill in your details:
    ```bash
    # .env
    JWT_SECRET_KEY="your_super_secret_jwt_key_here"
    OPENAI_API_KEY="sk-your-openai-api-key-here"
    SQLALCHEMY_DATABASE_URI="postgresql://openq_user:yourpassword@localhost:5432/openquantify"
    SENDER_EMAIL="your_email@gmail.com"
    SENDER_APP_PASSWORD="your_gmail_app_password"
    ```
    Alternatively, export them directly:
    ```bash
    export OPENAI_API_KEY=your-openai-api-key
    # ... export other variables ...
    ```
4.  Initialize Database (First time setup)
     Start PostgreSQL:** Ensure your PostgreSQL server is running.
        ```bash
        brew services start postgresql@14 # or `pg_ctl -D /path/to/your/data/cluster start`
        ```
      Create User and Database (if not already done):** Connect to `psql` as the `postgres` user and execute these commands.
        ```bash
        psql -U postgres
        ```
        Then, at the `postgres=#` prompt, paste:
        ```sql
        CREATE USER openq_user WITH PASSWORD 'postgres1234';
        CREATE DATABASE openquantify;
        GRANT ALL PRIVILEGES ON DATABASE openquantify TO openq_user;
        \q
        ```
     Create Tables:** Your Flask application will automatically create the tables defined in `models.py` when it starts up, thanks to `db.create_all()` in `main.py`.

5.  Run the App
    ```bash
    python main.py
    ```
    Server will start at `http://localhost:5000`

6.  **Verify Tables (Optional):**
    After the Flask app has run at least once, you can verify the tables in `openquantify`:
    ```bash
    psql -U openq_user -d openquantify
    # Enter 'postgres1234' (or your password) when prompted
    openquantify=> \dt
    # You should see tables like 'user' and 'ai_agents'
    openquantify=> \q
    ```

 API Endpoints Overview
`POST /recommend` – Input: `budget`, `use_case`, `preferred_specs` → Product recommendations
 `POST /compare` – Input: `product_ids` → Product comparison data
 `POST /summarize` – Input: `product_ids` → GPT-4o-mini generated summary & comparison of products
 `POST /delegate` – Input: `agent`, `task`, `parameters` → Response from delegated AI agent
 `GET /.well-known/ai-plugin.json` – Plugin manifest for ChatGPT discovery
 `GET /openapi.yaml` – OpenAPI spec documentation

 ChatGPT Plugin Integration
1.  Ensure your plugin is hosted and publicly accessible (e.g., on Render, Replit, Vercel).
2.  Your `ai-plugin.json` must be accessible at: `https://yourdomain.com/.well-known/ai-plugin.json`
3.  Your `openapi.yaml` must be accessible via the `api.url` specified in `ai-plugin.json`.

🛠️ To-Do
☐ Add user authentication (partially implemented in `auth.py`)
 ☐ Implement webhook triggers
 ☐ Add database support (MongoDB/PostgreSQL - PostgreSQL partially implemented)
 ☐ Expand agent skills (e.g. legal advice, health insights)
 ☐ Connect to frontend (React/Next.js or HTML)
 ☐ Deploy voice chatbot UI

👥 Contributors
 • Valencia Walker – Project Director / Developer
 • OpenQQuantify Team – Core AI Strategy
 • OpenAI Plugin API – Integration Framework

📄 License
This project is licensed under the MIT License. See LICENSE for more info.

📬 Contact
🔗 `https://www.openqquantify.com`
📧 `support@openqquantify.com`
📅 `https://calendly.com/openqquantifyexecutivemeeting/business`

