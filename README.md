# Astronomy-MCP Chatbot

## Project Overview
This project is a modular chatbot that integrates with Large Language Models (LLMs) using the Anthropic Claude API and supports the Model Context Protocol (MCP) for tool interoperability. The chatbot maintains conversational context, logs all interactions, and is designed to connect with both official and custom MCP servers.

## Features
- **LLM Integration:** Connects to Anthropic Claude via API for natural language conversations.
- **Context Management:** Maintains conversation history for contextual responses.
- **JSON Logging:** Logs all user and assistant interactions in a structured JSON file.
- **MCP Client Architecture:** Prepared to connect with official and custom MCP servers (Filesystem, Git, etc.).
- **Modular Design:** Codebase is organized for easy extension and maintenance.

## Implemented Functionalities
- Ask questions to the LLM and receive contextual answers.
- Maintain session context so follow-up questions are understood.
- Log all chat interactions in `chat_log.json`.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd astronomy-mcp
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirementx.txt
   ```

4. **Configure your API key:**
   - Copy `.env.example` to `.env` and add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     ```

## Usage

Run the chatbot interactively:
```bash
python chatbot/src/llm_client.py
```
- Type your questions in the console.
- Type `salir` to exit the chat.
- All interactions will be logged in `chat_log.json`.

## Directory Structure
```
astronomy-mcp/
├── chatbot/
│   ├── logs/
│   └── src/
│       ├── conversation_manager.py
│       ├── llm_client.py
│       ├── logger.py
│       ├── main.py
│       └── mcp_manager.py
├── requirementx.txt
├── .env.example
├── .gitignore
└── README.md
```

## Next Steps
- Integrate official MCP servers (Filesystem, Git) for tool-augmented conversations.
- Implement a custom MCP server for advanced functionalities.

## License
This project is for educational purposes.