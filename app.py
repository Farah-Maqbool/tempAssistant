
import streamlit as st

from llm import ask_assistant
from visualizer import (
    create_heatmap as create_heatmap_map,
    create_route_map,
    display_map
)


st.set_page_config(
    page_title="FortyGuard AI Assistant",
    page_icon="",
    layout="wide"
)

st.title("🌡️ FortyGuard AI Assistant")
st.caption(
    "Ask about environmental conditions, heatmaps, "
    "and temperature-aware routes."
)


# Ready-made test questions
questions = {
    "Environmental Conditions": (
        "What are the environmental conditions at latitude "
        "40.7128 and longitude -74.0060 in New York on "
        "November 23, 2026, at 2 PM? Use 32.5°C as the "
        "input temperature. Include temperature, humidity, "
        "heat index, and air quality."
    ),

    "Temperature Heatmap": (
        "Generate a temperature heatmap for this area in "
        "New York on November 23, 2026, at 2 PM. "
        "Use a granularity of 100. "
        "[[-74.0170, 40.7051], "
        "[-74.0031, 40.7051], "
        "[-74.0031, 40.7180], "
        "[-74.0170, 40.7180], "
        "[-74.0170, 40.7051]]"
    ),

    "Temperature-Aware Routing": (
        "Find a temperature-aware route from latitude "
        "40.7812, longitude -73.9665 to latitude 40.7580, "
        "longitude -73.9855 in New York, departing on "
        "November 24, 2026, at 9 AM UTC. Compare the "
        "Fastest, Balanced, and Coolest routes, including "
        "their distances, travel times, and temperatures."
    )
}


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# Extract visualization data
def prepare_visualization(data, visualization_type):

    if not data:
        return None

    if visualization_type == "heatmap":

        if "features" in data:
            return data

        return (
            data.get("data", {})
            .get("result", {})
            .get("map_data")
        )

    elif visualization_type == "routing":

        if "features" in data:
            return data

        return (
            data.get("data", {})
            .get("result", {})
            .get("result_routing")
        )

    return None


# Sidebar
with st.sidebar:
    st.title("About")

    st.write(
        "An AI assistant powered by FortyGuard APIs "
        "for environmental conditions, heatmaps, and "
        "temperature-aware routing."
    )

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()


# Ready-made questions
st.subheader("Try an example")

col1, col2, col3 = st.columns(3)

selected_prompt = None

with col1:
    if st.button("a) Environmental Conditions", use_container_width=True):
        selected_prompt = questions["Environmental Conditions"]

with col2:
    if st.button("b) Temperature Heatmap", use_container_width=True):
        selected_prompt = questions["Temperature Heatmap"]

with col3:
    if st.button("c) Temperature-Aware Route", use_container_width=True):
        selected_prompt = questions["Temperature-Aware Routing"]


# Chat input
typed_prompt = st.chat_input("Ask your own question...")

if typed_prompt:
    selected_prompt = typed_prompt


# Add new user message
if selected_prompt and st.session_state.pending_prompt is None:

    st.session_state.messages.append({
        "role": "user",
        "content": selected_prompt
    })

    st.session_state.pending_prompt = selected_prompt


# Display conversation history
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message["role"] == "assistant":

            data = message.get("visualization_data")
            visualization_type = message.get("visualization_type")

            if data:

                if visualization_type == "heatmap":

                    st.subheader("Temperature Heatmap")

                    map_obj = create_heatmap_map(data)

                    if map_obj:
                        display_map(map_obj)

                elif visualization_type == "routing":

                    st.subheader("Temperature-Aware Routes")

                    map_obj = create_route_map(data)

                    if map_obj:
                        display_map(map_obj)


# Process the new question AFTER displaying its user message
if st.session_state.pending_prompt:

    with st.chat_message("assistant"):

        with st.spinner("Analyzing your request..."):

            try:
                response = ask_assistant(
                    st.session_state.pending_prompt
                )

                answer = response.get(
                    "answer",
                    "I couldn't generate a response."
                )

                visualization_type = response.get(
                    "visualization_type"
                )

                raw_data = response.get(
                    "visualization_data"
                )

                visualization_data = prepare_visualization(
                    raw_data,
                    visualization_type
                )

                st.markdown(answer)

                if visualization_data:

                    if visualization_type == "heatmap":

                        st.subheader("Temperature Heatmap")

                        map_obj = create_heatmap_map(
                            visualization_data
                        )

                        if map_obj:
                            display_map(map_obj)

                    elif visualization_type == "routing":

                        st.subheader("Temperature-Aware Routes")

                        map_obj = create_route_map(
                            visualization_data
                        )

                        if map_obj:
                            display_map(map_obj)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "visualization_type": visualization_type,
                    "visualization_data": visualization_data
                })

            except Exception as e:

                error_message = f"Something went wrong: {str(e)}"

                st.error(error_message)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "visualization_type": None,
                    "visualization_data": None
                })

    st.session_state.pending_prompt = None
    st.rerun()
