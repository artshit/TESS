from src.core.ai_engine import AIEngine

def test_simple():
    ai = AIEngine()
    result = ai.process_input("Hello, test!")
    print(result)

if __name__ == "__main__":
    test_simple()
