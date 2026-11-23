
import folium
from streamlit_folium import st_folium


def create_heatmap(data):
    """
    Visualize FortyGuard heatmap GeoJSON data.
    Expected input: map_data FeatureCollection.
    """

    features = data.get("features", [])

    if not features:
        return None

    # Get map center from the first polygon
    first_coords = features[0]["geometry"]["coordinates"][0]
    center_lon = sum(point[0] for point in first_coords) / len(first_coords)
    center_lat = sum(point[1] for point in first_coords) / len(first_coords)

    map_obj = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles="OpenStreetMap"
    )

    temperatures = [
        feature["properties"]["average_temperature"]
        for feature in features
        if feature.get("properties", {}).get("average_temperature") is not None
    ]

    if not temperatures:
        return map_obj

    min_temp = min(temperatures)
    max_temp = max(temperatures)

    def get_color(temp):
        ratio = (
            (temp - min_temp) / (max_temp - min_temp)
            if max_temp != min_temp else 0.5
        )

        if ratio < 0.33:
            return "#2c7bb6"
        elif ratio < 0.66:
            return "#fdae61"
        return "#d7191c"

    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        avg = properties.get("average_temperature")
        if avg is None or geometry.get("type") != "Polygon":
            continue

            # GeoJSON coordinates: [longitude, latitude]
        tooltip_html = f"""
        <b>Tile:</b> {properties.get('tile_id', 'N/A')}<br>
        <b>Average:</b> {avg:.2f} °C<br>
        <b>Minimum:</b> {properties.get('min_temperature', 'N/A')} °C<br>
        <b>Maximum:</b> {properties.get('max_temperature', 'N/A')} °C
        """

        folium.GeoJson(
            feature,
            style_function=lambda f, temp=avg: {
                "fillColor": get_color(temp),
                "color": "#444444",
                "weight": 0.3,
                "fillOpacity": 0.75
            },
            tooltip=folium.Tooltip(tooltip_html)
        ).add_to(map_obj)

    return map_obj


def create_route_map(data):
    """
    Visualize FortyGuard temperature-aware routing alternatives.
    Expected input: result_routing FeatureCollection.
    """

    features = data.get("features", [])

    if not features:
        return None

    colors = {
        "Fastest": "#2878B5",
        "Balanced": "#E69F00",
        "Coolest": "#269B55"
    }

    map_obj = folium.Map(
        location=[40.758, -73.9855],
        zoom_start=14,
        tiles="OpenStreetMap"
    )

    all_coordinates = []

    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        if geometry.get("type") != "LineString":
            continue

        coordinates = geometry.get("coordinates", [])

        if not coordinates:
            continue

        # Convert [longitude, latitude] to [latitude, longitude]
        route_points = [
            [lat, lon] for lon, lat in coordinates
        ]

        all_coordinates.extend(route_points)

        label = properties.get("label", "Route")
        selected = properties.get("selected", False)

        color = colors.get(label, "#777777")

        thermal = properties.get("thermal", {})

        popup_html = f"""
        <b>{label}</b><br>
        <b>Selected:</b> {selected}<br>
        <b>Score:</b> {properties.get('score', 'N/A')}<br>
        <b>Distance:</b> {properties.get('distance_km', 'N/A')} km<br>
        <b>Duration:</b> {properties.get('duration_min', 'N/A')} min<br>
        <b>Mean temperature:</b> {thermal.get('mean_c', 'N/A')} °C<br>
        <b>Peak temperature:</b> {thermal.get('peak_c', 'N/A')} °C
        """

        folium.PolyLine(
            locations=route_points,
            color=color,
            weight=7 if selected else 4,
            opacity=1 if selected else 0.75,
            tooltip=f"{label} - {properties.get('distance_km', 'N/A')} km",
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(map_obj)

    if all_coordinates:
        # Mark route start and destination
        folium.Marker(
            all_coordinates[0],
            tooltip="Start",
            icon=folium.Icon(color="green", icon="play")
        ).add_to(map_obj)

        folium.Marker(
            all_coordinates[-1],
            tooltip="Destination",
            icon=folium.Icon(color="red", icon="flag")
        ).add_to(map_obj)

        map_obj.fit_bounds(all_coordinates)

    return map_obj


def display_map(map_obj, height=550):
    """Display a Folium map in Streamlit."""

    if map_obj:
        st_folium(
            map_obj,
            width=None,
            height=height,
            returned_objects=[]
        )
