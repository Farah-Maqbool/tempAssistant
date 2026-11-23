import streamlit as st
from api import get_temperature_aware_route, check_activity_status
from visualizer import create_route_map, display_map
import time

st.title("Temperature-Aware Routing Test")

if st.button("Generate Routes"):

    origin = {
        "lat": 40.7812,
        "lon": -73.9665
    }

    destination = {
        "lat": 40.7580,
        "lon": -73.9855
    }

    departure_time = "2026-11-24T09:00:00Z"

    with st.spinner("Requesting routes..."):
        response = get_temperature_aware_route(
            origin,
            destination,
            departure_time
        )

    if response:
        activity_id = response.get("data", {}).get("activity_id")

        if activity_id:
            with st.spinner("Waiting for routing results..."):
                while True:
                    response = check_activity_status(activity_id)
                    status = response.get("data", {}).get("status")

                    if status == "Completed":
                        break

                    if status == "Failed":
                        st.error("Routing request failed.")
                        st.json(response)
                        st.stop()

                    time.sleep(3)

        result = response.get("data", {}).get("result", {})
        routing_data = result.get("result_routing")

        if routing_data:
            st.success("Routes generated successfully!")

            map_obj = create_route_map(routing_data)
            display_map(map_obj)

            st.subheader("Route Details")

            for feature in routing_data.get("features", []):
                properties = feature.get("properties", {})
                thermal = properties.get("thermal", {})

                st.write(f"**{properties.get('label', 'Route')}**")
                st.write(f"Selected: {properties.get('selected', False)}")
                st.write(f"Distance: {properties.get('distance_km')} km")
                st.write(f"Duration: {properties.get('duration_min')} minutes")
                st.write(f"Mean temperature: {thermal.get('mean_c')} °C")
                st.divider()

        else:
            st.error("Routing data was not found.")
            st.json(response)

    else:
        st.error("Could not generate routes.")