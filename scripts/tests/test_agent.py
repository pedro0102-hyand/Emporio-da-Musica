import os
import sys
import unittest
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

load_dotenv()
from src.agent import build_agent

class TestEmporioAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api_key = os.getenv("GROQ_API_KEY")
        if not cls.api_key:
            raise unittest.SkipTest("⚠️ GROQ_API_KEY não encontrada no .env. Testes de integração ignorados.")

        print("🤖 Inicializando o agente da Empório da Música para os testes...")
        cls.agent = build_agent()

    def test_01_search_products_tool(self):
        
        print("\n🧪 Teste 1: Consulta de catálogo (Violões até R$ 1000)...")
        config = {"configurable": {"thread_id": "test_thread_1"}}
        inputs = {"messages": [("user", "Quais opções de violões disponíveis custando até R$ 1000?")]}
        
        response = self.agent.invoke(inputs, config=config)
        last_message = response["messages"][-1].content
        self.assertIsNotNone(last_message)
        self.assertTrue(len(last_message) > 0)
        print(f"✅ Resposta do Agente:\n{last_message}\n")

    def test_02_order_status_tool(self):
       
        print("🧪 Teste 2: Consulta de status de pedido...")
        config = {"configurable": {"thread_id": "test_thread_2"}}
        inputs = {"messages": [("user", "Qual o status do meu pedido número 1?")]}

        response = self.agent.invoke(inputs, config=config)
        last_message = response["messages"][-1].content        
        self.assertIsNotNone(last_message)
        self.assertTrue(len(last_message) > 0)
        print(f"✅ Resposta do Agente:\n{last_message}\n")

    def test_03_rag_policies_tool(self):
        
        print("🧪 Teste 3: Consulta RAG de políticas (Devolução e Arrependimento)...")
        config = {"configurable": {"thread_id": "test_thread_3"}}
        inputs = {"messages": [("user", "Me arrependi da minha compra online, posso devolver o pedido?")]}
        
        response = self.agent.invoke(inputs, config=config)
        last_message = response["messages"][-1].content
        self.assertIsNotNone(last_message)
        self.assertTrue(any(term in last_message.lower() for term in ["7 dias", "arrependimento", "devolução"]))
        print(f"✅ Resposta do Agente:\n{last_message}\n")

    def test_04_out_of_scope_guardrail(self):
       
        print("🧪 Teste 4: Pergunta fora de escopo (Guardrail)...")
        config = {"configurable": {"thread_id": "test_thread_4"}}
        inputs = {"messages": [("user", "Como faço para programar um robô em Python?")]}
        
        response = self.agent.invoke(inputs, config=config)
        last_message = response["messages"][-1].content
        self.assertIsNotNone(last_message)
        print(f"✅ Resposta do Agente:\n{last_message}\n")

    def test_05_memory_persistence(self):
      
        print("🧪 Teste 5: Memória contextual da sessão...")
        config = {"configurable": {"thread_id": "test_thread_5"}}
        
        inputs_1 = {"messages": [("user", "Olá! Meu nome é Gabriel e procuro um violão da Yamaha.")]}
        self.agent.invoke(inputs_1, config=config)
        
        inputs_2 = {"messages": [("user", "Qual é o meu nome e o que eu estava procurando?")]}
        response_2 = self.agent.invoke(inputs_2, config=config)
        last_message = response_2["messages"][-1].content
        self.assertIn("Gabriel", last_message)
        print(f"✅ Resposta com memória mantida:\n{last_message}\n")

if __name__ == "__main__":
    unittest.main()