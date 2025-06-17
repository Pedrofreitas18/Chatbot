from .flow import FlowManager
import requests
import re
from ..logic.cadastro import cadastro_logic
from ..logic.cardapio import cardapio_logic
from ..logic.pedido import pedido_logic

INTENT_CONFIG = {
    "cadastro": {
        "fields": ["name", "number", "street", "city", "state"],
        "context": "Você é responsável por cadastrar um novo cliente.",
        "logic": cadastro_logic,
    },
    "cardapio": {
        "fields": [],
        "context": "Você é responsável por mostrar o cardápio.",
        "logic": cardapio_logic,
    },
    "pedido": {
        "fields": ["item", "quantidade"],
        "context": "Você está recebendo um pedido do cliente.",
        "logic": pedido_logic,
    }
}

def detect_intent(user_message: str) -> str:
    prompt = f"""
Você é um assistente que classifica a intenção de uma mensagem de um usuário.

Mensagens como:
- "Quero fazer um pedido" → intent: pedido
- "Qual é o cardápio?" → intent: cardapio
- "Meu nome é João" → intent: cadastro
- "Meu CEP é 01310-100" → intent: cadastro
- "Fechar pedido" → intent: checkout

Classifique a intenção da seguinte mensagem:
"{user_message}"

Retorne apenas a intenção (ex: cadastro, pedido, cardapio, checkout).
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "openchat", "prompt": prompt, "stream": False}
    )

    result = response.json()["response"]
    
    # Sanitiza para pegar só a palavra-chave
    match = re.search(r'(cadastro|pedido|cardapio|checkout)', result.lower())
    return match.group() if match else "desconhecido"
