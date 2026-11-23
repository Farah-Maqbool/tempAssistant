
import os
import json
import time

from groq import Groq
from dotenv import load_dotenv

from api import (
    get_environmental_parameters,
    create_heatmap,
    get_temperature_aware_route,
    check_activity_status
)

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"


# Wait for a FortyGuard activity to finish
def wait_for_activity(activity_id, max_wait=600):

    start_time = time.time()

    while time.time() - start_time < max_wait:

        result = check_activity_status(activity_id)

        status = result.get("data", {}).get("status")

        print("FortyGuard activity:", status)

        if status == "Completed":
            return result

        if status == "Failed":
            raise Exception(f"FortyGuard activity failed: {result}")

        time.sleep(10)

    raise TimeoutError("FortyGuard activity timed out.")


# Submit a request and retrieve its completed result
def submit_and_wait(submission):

    if submission.get("error"):
        raise Exception(submission)

    activity_id = submission["data"]["activity_id"]

    return wait_for_activity(activity_id)


# Remove large geographic data before sending results to the LLM
def compact_result(data):

    excluded_keys = {
        "geometry",
        "coordinates",
        "map_data",
        "features",
        "polyline",
        "encoded_polyline"
    }

    if isinstance(data, dict):

        return {
            key: compact_result(value)
            for key, value in data.items()
            if key.lower() not in excluded_keys
        }

    if isinstance(data, list):

        if len(data) > 15:
            return [compact_result(item) for item in data[:15]]

        return [compact_result(item) for item in data]

    return data


# Available functions for the LLM
tools = [

    {
        "type": "function",
        "function": {
            "name": "get_environmental_parameters",
            "description": (
                "Get environmental measurements for a location "
                "at a specific date and time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "temperature": {"type": "number"},
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Time in HH:MM format"
                    }
                },
                "required": [
                    "latitude",
                    "longitude",
                    "temperature",
                    "date"
                ],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_heatmap",
            "description": (
                "Generate a temperature heatmap for a geographic "
                "polygon and a specific date and time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "polygon": {
                        "type": "object",
                        "description": "GeoJSON Polygon",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["Polygon"]
                            },
                            "coordinates": {
                                "type": "array",
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "array",
                                        "items": {"type": "number"}
                                    }
                                }
                            }
                        },
                        "required": ["type", "coordinates"],
                        "additionalProperties": False
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Time in HH:MM format"
                    },
                    "granularity": {
                        "type": "integer",
                        "enum": [20, 60, 80, 100]
                    }
                },
                "required": ["polygon", "date"],
                "additionalProperties": False
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "get_temperature_aware_route",
            "description": (
                "Find temperature-aware driving routes between "
                "an origin and destination."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lon": {"type": "number"}
                        },
                        "required": ["lat", "lon"],
                        "additionalProperties": False
                    },
                    "destination": {
                        "type": "object",
                        "properties": {
                            "lat": {"type": "number"},
                            "lon": {"type": "number"}
                        },
                        "required": ["lat", "lon"],
                        "additionalProperties": False
                    },
                    "departure_time": {
                        "type": "string",
                        "description": "ISO-8601 datetime"
                    }
                },
                "required": [
                    "origin",
                    "destination",
                    "departure_time"
                ],
                "additionalProperties": False
            }
        }
    }
]


# Execute the selected Python function
def execute_function(name, arguments):

    if name == "get_environmental_parameters":

        submission = get_environmental_parameters(**arguments)
        result = submit_and_wait(submission)

        return compact_result(result), None, None

    elif name == "create_heatmap":

        submission = create_heatmap(
            polygon=arguments["polygon"],
            date=arguments["date"],
            start_time=arguments.get("start_time", "14:00"),
            granularity=arguments.get("granularity", 100)
        )

        result = submit_and_wait(submission)

        # Keep the complete map response for the visualizer.
        # Never send its large GeoJSON to the LLM.
        return (
            "The heatmap was generated successfully. "
            "Its geographic data is ready for visualization.",
            result,
            "heatmap"
        )

    elif name == "get_temperature_aware_route":

        submission = get_temperature_aware_route(**arguments)
        result = submit_and_wait(submission)

        return compact_result(result), result, "routing"

    raise ValueError(f"Unknown function: {name}")


# Main assistant function
def ask_assistant(user_message):

    messages = [
        {
            "role": "system",
            "content": """
You are a FortyGuard temperature and environmental assistant.

You have access to three functions:

1. Environmental Parameters:
   Retrieve environmental measurements for a location.

2. Create Heatmap:
   Generate a temperature heatmap for a geographic area.

3. Temperature-Aware Routing:
   Find temperature-aware driving routes.

Instructions:
- Understand the user's request and select the appropriate function.
- Ask for missing required information before calling a function.
- Never invent coordinates, dates, temperatures, or polygon boundaries.
- Use only the provided functions to retrieve FortyGuard data.
- Explain returned measurements clearly and briefly.
- For routing, explain useful route information from the returned data.
- For heatmaps, tell the user when the map is ready to view.
- Never claim an API request succeeded before receiving its result.
- Do not invent environmental measurements or route details.
"""
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    visualization_data = None
    visualization_type = None

    for _ in range(3):

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            parallel_tool_calls=False,
            temperature=0.2
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            return {
                "answer": assistant_message.content,
                "visualization_data": visualization_data,
                "visualization_type": visualization_type
            }

        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        for tool_call in assistant_message.tool_calls:

            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            print("Selected function:", function_name)
            print("Arguments:", arguments)

            result, visual_data, visual_type = execute_function(
                function_name,
                arguments
            )

            if visual_data is not None:
                visualization_data = visual_data
                visualization_type = visual_type

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    return {
        "answer": "I couldn't complete the request. Please try again.",
        "visualization_data": visualization_data,
        "visualization_type": visualization_type
    }
