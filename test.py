from llm import ask_assistant
from pprint import pprint

response = ask_assistant(
    """
    Find a temperature-aware driving route.

    Origin: latitude 40.7812, longitude -73.9665
    Destination: latitude 40.7580, longitude -73.9855
    Departure time: 2026-11-24T09:00:00Z
    """
)

print("\n========== ROUTING API RESPONSE ==========\n")
pprint(response["visualization_data"], sort_dicts=False, width=120)