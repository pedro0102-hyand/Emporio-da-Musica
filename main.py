import os
import sys
import uuid
from dotenv import load_dotenv

load_dotenv()
from src.agent import build_agent


def run_cli():
    print("=" * 60)
    print("🎸 EMPÓRIO DA MÚSICA - ASSISTENTE VIRTUAL DE ATENDIMENTO 🎸")
    print("=" * 60)
    print("Digite 'sair' ou 'exit' para encerrar a conversa.\n")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ Erro: GROQ_API_KEY não foi encontrada no arquivo .env!")
        print("Por favor, adicione sua chave da Groq ao .env antes de iniciar.")
        sys.exit(1)

    agent = build_agent()
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    print("🟢 Atendimento iniciado! Como posso ajudar você hoje?\n")

    while True:
        try:
            user_input = input("👤 Você: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["sair", "exit", "quit"]:
                print("\n🤖 Agente: Obrigado por entrar em contato com a Empório da Música! Até logo!")
                break

            inputs = {"messages": [("user", user_input)]}
            response = agent.invoke(inputs, config=config)
            bot_response = response["messages"][-1].content
            print(f"\n🤖 Agente: {bot_response}\n")

        except KeyboardInterrupt:
            print("\n\n🤖 Agente: Atendimento encerrado. Tenha um ótimo dia!")
            break
        except Exception as e:
            print(f"\n❌ Ocorreu um erro durante o processamento: {e}\n")


if __name__ == "__main__":
    run_cli()