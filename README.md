# MCP Chatbot for F1 and Astronomy

## 1. Project Overview

This project is a chatbot designed to demonstrate the modularity of the Model Context Protocol (MCP). The chatbot can connect to external MCP servers and also runs its own local MCP server for astronomical calculations.

It runs a self-contained, multi-tool Astronomy server.


## 2. Requirements & Installation

Follow these steps to set up and run the project.

### 2.1. Prerequisites

- Python 3.10+
- An Anthropic API key (for optional LLM functionalities)

### 2.2. Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd REDES_PRY1
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    The project's dependencies are listed in `requirementx.txt`. Install them using pip:
    ```bash
    pip install -r requirementx.txt
    ```

4.  **Configure your API key (Optional):**
    If you plan to use LLM functionalities, copy `.env.example` to `.env` and add your Anthropic API key:
    ```
    ANTHROPIC_API_KEY=your_api_key_here
    ```

## 3. How to Run the Chatbot

To start the main application, run the `main.py` script from the root directory:

```bash
python3 chatbot/src/main.py
```

This will launch a menu where you can navigate to the different MCP functionalities.

## 4. MCP Functionality

This project implements both a local server and a client for an external server.

### 4.1. Astronomy MCP Server (Local)

The chatbot includes its own powerful, local MCP server for providing astronomical data. The server runs automatically when you access the "Astronomía" menu in the chatbot.

#### Specification

The server (`eclipse-calculator-db`) provides tools to query a curated internal database of solar and lunar eclipses.

#### Available Tools

1.  **`list_eclipses_by_year`**
    -   **Description:** Lists all eclipses stored in the database for a given year.
    -   **Parameters:**
        -   `year` (integer): The year you want to query.
    -   **Example Usage (via Chatbot Menu):**
        1.  Select option "1. Listar eclipses por año".
        2.  Enter the year (e.g., `2026`).
        3.  The chatbot will display a table with the date, type, description, and visibility locations for all eclipses in that year.

2.  **`calculate_eclipse_visibility`**
    -   **Description:** Checks if a specific eclipse is visible from a specific location and provides details.
    -   **Parameters:**
        -   `date` (string): The date of the eclipse in `YYYY-MM-DD` format.
        -   `location` (string): The name of the city (e.g., `Guatemala City`, `Madrid`).
    -   **Example Usage (via Chatbot Menu):**
        1.  Select option "2. Verificar visibilidad de eclipse".
        2.  Enter the date (e.g., `2026-08-12`).
        3.  Enter the location (e.g., `Madrid`).

3.  **`predict_next_eclipse`**
    -   **Description:** Finds the next eclipse in the database visible from a given location.
    -   **Parameters:**
        -   `location` (string): The name of the city.
    -   **Example Usage (via Chatbot Menu):**
        1.  Select option "3. Predecir próximo eclipse visible".
        2.  Enter the location (e.g., `Guatemala City`).
