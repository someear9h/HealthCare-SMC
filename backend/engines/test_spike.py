from engines.spike_engine import detect_outbreaks

if __name__ == "__main__":

    outbreaks = detect_outbreaks()

    print("\n🚨 DETECTED OUTBREAKS:\n")

    print(outbreaks.head(20))

    print(f"\nTotal outbreaks detected: {len(outbreaks)}")
