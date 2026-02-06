from engines.spike_engine import detect_outbreaks, explain_outbreak

if __name__ == "__main__":

    outbreaks = detect_outbreaks()

    print("\n🚨 DETECTED OUTBREAKS:\n")

    print(outbreaks.head(20))

    print(f"\nTotal outbreaks detected: {len(outbreaks)}")

    for _, row in outbreaks.head(5).iterrows():
        print(explain_outbreak(row))