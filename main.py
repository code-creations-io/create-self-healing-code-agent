import sys, dotenv
from agents.orchestrator import self_correcting_loop

dotenv.load_dotenv() # loads .env into environment

if __name__ == "__main__":
    spec = sys.argv[1] if len(sys.argv) > 1 else "Write fibonacci(n)"
    final_code = self_correcting_loop(spec)
    print("\n✅  ALL TESTS PASS.  Final code ↓\n")
    print(final_code)