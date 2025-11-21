import os
import sys
import django
from pathlib import Path

# Setup Django environment
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemviz_backend.settings')
django.setup()

from equipment.services import generate_ai_insights, AIGenerationError

def test():
    print("Testing generate_ai_insights...")
    summary = {
        'total_count': 10,
        'avg_flowrate': 50.5,
        'avg_pressure': 2.3,
        'avg_temperature': 100.0,
        'type_distribution': {'Pump': 5, 'Valve': 5}
    }
    
    try:
        insights = generate_ai_insights(summary)
        print(f"SUCCESS: Insights generated (Length: {len(insights)})")
        print("-" * 20)
        print(insights)
        print("-" * 20)
    except AIGenerationError as e:
        print(f"EXPECTED ERROR: {e}")
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test()
