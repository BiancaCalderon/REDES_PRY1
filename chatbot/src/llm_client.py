from dotenv import load_dotenv
import os
import json
from datetime import datetime
import anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
LOG_FILE = "chat_log.json"

# Instanciar el cliente oficial de Anthropic
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def ask_claude(messages, model="claude-sonnet-4-20250514", max_tokens=4096, tools=None):
    """Llama a la API de Claude usando la librería oficial, con soporte para herramientas."""
    try:
        request_args = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if tools:
            request_args["tools"] = tools

        response = client.messages.create(**request_args)
        
        # Devolvemos la respuesta como un diccionario para mantener la compatibilidad
        return response.model_dump()
    except Exception as e:
        print(f"Error al llamar a la API de Claude: {e}")
        # Devolver un error en un formato compatible
        return {
            "type": "error",
            "error": {"type": "api_error", "message": str(e)}
        }

def log_interaction_json(user_message, assistant_message):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user": user_message,
        "assistant": assistant_message
    }
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
    """Función de prueba para el cliente de LLM."""
    print("¡Bienvenido al chat con Claude! Escribe 'salir' para terminar.\n")
    messages = []
    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("¡Hasta luego!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            result = ask_claude(messages)
            
            if result.get('type') == 'error':
                print(f"Error: {result['error']['message']}")
                messages.pop() # Eliminar el último mensaje de usuario si hubo un error
                continue

            # Extrae la respuesta del asistente
            response_text = ""
            for content_block in result.get("content", []):
                if content_block.get("type") == "text":
                    response_text += content_block["text"]
            
            if not response_text:
                response_text = "[Sin respuesta de texto]"

            print(f"Claude: {response_text}")

            # Añade la respuesta del asistente al historial
            messages.append({"role": "assistant", "content": response_text})
            log_interaction_json(user_input, response_text)

        except Exception as e:
            print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()