# safe_infinite_print.py
import time

def main():
    i = 0
    try:
        while True:
            i += 1
            print(f"Iteration {i} — press Ctrl+C to stop")
            time.sleep(1)  # sleep keeps CPU usage minimal
    except KeyboardInterrupt:
        print("\nStopped by user (KeyboardInterrupt). Goodbye!")

if __name__ == "__main__":
    main()
