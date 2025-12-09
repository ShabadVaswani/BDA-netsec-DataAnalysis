import fitdecode
import os
from datetime import datetime

# Path to the file known to have respiration data
TEST_FILE = 'data/garmin/2025-11-05/380127734123_WELLNESS.fit'

def verify_respiration():
    print(f"🔍 Verifying respiration data in: {TEST_FILE}")
    
    if not os.path.exists(TEST_FILE):
        print("❌ File not found!")
        return

    respiration_count = 0
    stress_count = 0
    monitoring_count = 0
    
    with fitdecode.FitReader(TEST_FILE) as fit:
        for frame in fit:
            if isinstance(frame, fitdecode.FitDataMessage):
                if frame.name == 'respiration_rate':
                    respiration_count += 1
                    if respiration_count <= 3:
                        print(f"\n✅ Found Respiration Rate record #{respiration_count}:")
                        for field in frame.fields:
                            print(f"   - {field.name}: {field.value} {field.units if field.units else ''}")
                
                elif frame.name == 'stress_level':
                    stress_count += 1
                
                elif frame.name == 'monitoring':
                    monitoring_count += 1

    print("\n" + "="*40)
    print(f"📊 Summary:")
    print(f"   - Respiration Rate records: {respiration_count}")
    print(f"   - Stress Level records: {stress_count}")
    print(f"   - Monitoring records: {monitoring_count}")
    print("="*40)

    if respiration_count > 0:
        print("\n✅ SUCCESS: Respiration data is accessible via fitdecode!")
    else:
        print("\n❌ FAILURE: Still no respiration data found.")

if __name__ == "__main__":
    verify_respiration()
