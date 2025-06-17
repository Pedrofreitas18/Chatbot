from django.shortcuts import render
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
import json
from .models import CardapioItem
from .models import User
from .models import Address
from .nlp.openchat_interface import gerar_resposta_local
from .nlp.openchat_interface import extract_user_data_from_text
from .core.flow import FlowManager
from .models import MessageHistory
from .models import get_last_messages
from .core.intent_router import detect_intent, INTENT_CONFIG


# Create your views here.
def home(request):
    return render(request, 'teste/home.html')

@method_decorator(csrf_exempt, name='dispatch')
class WhatsAppWebhookView(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        numero = data.get("from")  # número do usuário
        mensagem = data.get("message")  # mensagem recebida

        # Busca o cardápio no banco
        cardapio = CardapioItem.objects.all()
        itens = "\n".join([f"- {item.nome} (R${item.preco})" for item in cardapio])

        prompt_contexto = (
            f"Você é um atendente virtual da Pizzaria Bom Sabor. "
            f"Este é o cardápio atual:\n{itens}\n"
            "Ajude o cliente a escolher, tire dúvidas e registre o pedido."
        )

        resposta_bot = gerar_resposta_local(mensagem, contexto=prompt_contexto)

        return JsonResponse({"resposta": resposta_bot})

@method_decorator(csrf_exempt, name='dispatch')
class CadastroViaIAView(View):

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        text = data.get("message")

        extracted = extract_user_data_from_text(text)

        if not extracted:
            return JsonResponse({"error": "Não foi possível extrair os dados."}, status=400)

        user = User.objects.create(
            name=extracted["name"],
            number=extracted["number"]
        )

        Address.objects.create(
            user=user,
            street=extracted["address"]["street"],
            number=extracted["address"]["number"],
            complement=extracted["address"]["complement"],
            neighborhood=extracted["address"]["neighborhood"],
            city=extracted["address"]["city"],
            state=extracted["address"]["state"],
            zip_code=extracted["address"]["zip_code"]
        )

        return JsonResponse({"message": f"{user.name}, seus dados foram salvos com sucesso!"})

@method_decorator(csrf_exempt, name='dispatch')
class NLPWebhookView(View):
    def post(self, request):
        data = json.loads(request.body)
        message = data.get("message", "")
        user_number  = data.get("from", "")

        # Exemplo: cadastro de cliente
        manager = FlowManager(
            flow_name="cadastro_cliente",
            context="Você é um atendente de cadastro. Extraia os dados para registrar um novo cliente.",
            expected_fields=["name", "number", "street", "number", "city", "state", "zip_code"]
        )

        result = manager.process_message(message, user_number)

        # Aqui você pode salvar no banco se quiser
        return JsonResponse({"dados_extraidos": result})

@method_decorator(csrf_exempt, name='dispatch')
class NameOnlyNLPView(View):
    def post(self, request):
        data = json.loads(request.body)
        message = data.get("message", "")
        user_number = data.get("from", "")

        MessageHistory.objects.create(
            sender="user",
            user_number=user_number,
            message=message,
        )

        manager = FlowManager(
            flow_name="descobrir_nome",
            context="Você é um sistema que precisa descobrir o nome completo do usuário a partir da mensagem.",
            expected_fields=["name"]
        )

        result = manager.process_message(message, user_number)
        MessageHistory.objects.create(
            sender="bot",
            user_number=user_number,
            message=result.get("name", "Nome não encontrado"),
        )

        return JsonResponse({"extracted_name": result.get("name", "Nome não encontrado")})
    
def nlp_view_factory(manager: FlowManager, business_logic_fn):
    @method_decorator(csrf_exempt, name='dispatch')
    class ParametrizedNLPView(View):
        def post(self, request):
            data = json.loads(request.body)
            message = data.get("message", "")
            user_number = data.get("from", "")

            # Save user message
            MessageHistory.objects.create(
                sender="user",
                user_number=user_number,
                message=message,
            )

            # Process message with NLP
            result = manager.process_message(message, user_number)

            # Execute business logic
            response_text = business_logic_fn(result, user_number)

            # Save bot response
            MessageHistory.objects.create(
                sender="bot",
                user_number=user_number,
                message=response_text,
            )

            return JsonResponse({"message": response_text})

    return ParametrizedNLPView.as_view()


@method_decorator(csrf_exempt, name='dispatch')
class GenericNLPView(View):
    def post(self, request):
        data = json.loads(request.body)
        message = data.get("message", "")
        user_number = data.get("from", "")

        # Armazena mensagem recebida
        MessageHistory.objects.create(
            sender="user", user_number=user_number, message=message
        )

        # Detecta intenção
        intent = detect_intent(message)
        config = INTENT_CONFIG[intent]

        manager = FlowManager(
            flow_name=intent,
            context=config["context"],
            expected_fields=config["fields"]
        )

        result = manager.process_message(message, user_number)

        # Executa lógica correspondente
        response_text = config["logic"](result, user_number)

        # Armazena resposta
        MessageHistory.objects.create(
            sender="bot", user_number=user_number, message=response_text
        )

        return JsonResponse({"intent": intent, "response": response_text, "data": result})