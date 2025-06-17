from flow import FlowManager

cadastro_manager = FlowManager(
    flow_name="cadastro_cliente",
    context="Você é um atendente de cadastro.",
    expected_fields=["name", "number"]
)

