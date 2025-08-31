from dotenv import load_dotenv
import os
import requests
import json
from datetime import datetime

load_dotenv()

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LOG_FILE = "chat_log.json"

def ask_claude(messages, model="claude-sonnet-4-20250514", max_tokens=1024):
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages
    }
    response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data)
    response.raise_for_status()
    return response.json()

def log_interaction_json(user_message, assistant_message):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "assistant": assistant_message
    }
    # Leer el log existente o crear uno nuevo
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                log_data = json.load(f)
            except json.JSONDecodeError:
                log_data = []
    else:
        log_data = []
    log_data.append(log_entry)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def main():
    print("¡Bienvenido al chat con Claude! Escribe 'salir' para terminar.\n")
    messages = []
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("¡Hasta luego!")
            break

        # Añade el mensaje del usuario al historial
        messages.append({"role": "user", "content": user_input})

        # Llama al modelo con todo el historial
        try:
            result = ask_claude(messages)
            # Extrae la respuesta del asistente
            if "content" in result and result["content"]:
                assistant_message = result["content"][0]["text"]
            else:
                assistant_message = "[Sin respuesta]"

            print(f"Claude: {assistant_message}")

            # Añade la respuesta del asistente al historial
            messages.append({"role": "assistant", "content": assistant_message})

            # Log de la interacción en formato JSON
            log_interaction_json(user_input, assistant_message)

        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
