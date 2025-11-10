<<<<<<< HEAD
from src.core.AIEngine import AIEngine
=======
from src.core.ai_engine import AIEngine
>>>>>>> 3115e64782de9e5c0302baebf3995aa4b3a8e45f

def test_simple():
    ai = AIEngine()
    result = ai.process_input("Hello, test!")
    print(result)

if __name__ == "__main__":
    test_simple()
