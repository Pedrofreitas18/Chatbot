import requests
import json

def gerar_resposta_local(mensagem_usuario, contexto="Você é um atendente simpático da Pizzaria Bom Sabor."):
    try:
        resposta = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "openchat",
                "prompt": f"{contexto}\nUsuário: {mensagem_usuario}\nBot:",
                "stream": False
            }
        )
        resposta.raise_for_status()
        return resposta.json()["response"].strip()
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"
    
def extract_user_data_from_text(text):
    prompt = f"""
Você é um assistente que extrai dados estruturados de cadastro a partir de um texto enviado pelo usuário.

Texto do usuário:
\"\"\"{text}\"\"\"

Extraia os seguintes campos e devolva em JSON:
- name (nome completo)
- number (telefone, somente números)
- address:
    - street (rua)
    - number (número)
    - complement (complemento, se houver)
    - neighborhood (bairro)
    - city (cidade)
    - state (estado - 2 letras)
    - zip_code (CEP)

Se não conseguir identificar algum campo, deixe-o vazio.

Responda apenas com o JSON.
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "openchat", "prompt": prompt, "stream": False}
    )

    result = response.json()["response"].strip()

    try:
        return json.loads(result)
    except Exception as e:
        print("Erro ao processar resposta da IA:", e)
        return None
