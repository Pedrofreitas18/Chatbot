from django.urls import path
from .views import WhatsAppWebhookView
from .views import CadastroViaIAView
from .views import NameOnlyNLPView
from .views import nlp_view_factory
from .views import GenericNLPView
from .core.flow import FlowManager


def cadastro_logic(result, user_number):
    name = result.get("name")
    return f"Cadastro realizado para {name}!"

cadastro_manager = FlowManager(
    flow_name="cadastro_cliente",
    context="Você é um atendente de cadastro.",
    expected_fields=["name", "number"]
)

urlpatterns = [
    path('webhook/', WhatsAppWebhookView.as_view(), name='whatsapp_webhook'),
    path('webhooktest/', CadastroViaIAView.as_view(), name='whatsapp_webhooktest'),
    path('get-name/', NameOnlyNLPView.as_view(), name='get_name'),
    path("cadastro/", nlp_view_factory(cadastro_manager, cadastro_logic)),
    path("chat/", GenericNLPView.as_view()),
]
