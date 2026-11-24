
# FortyGuard AI Assistant 

An AI-powered assistant that uses FortyGuard APIs to retrieve environmental data, generate temperature heatmaps, and find temperature-aware routes.

## Features

- **Environmental Analysis:** Retrieve temperature, humidity, heat index, and air quality data.
- **Temperature Heatmaps:** Generate interactive heatmaps for selected geographical areas.
- **Temperature-Aware Routing:** Compare Fastest, Balanced, and Coolest routes.
- **LLM Integration:** Understand natural-language queries using Groq.

## Tech Stack

- Python 3.11
- Streamlit
- Groq LLM
- FortyGuard APIs
- Folium

## Setup

1. Clone the repository:

   ```bash
   git clone YOUR_REPOSITORY_URL
   cd tempAssistant
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file:

   ```env
   FORTYGUARD_API_KEY=your_api_key
   GROQ_API_KEY=your_api_key
   ```

4. Run the application:

   ```bash
   streamlit run app.py
   ```

## Live Demo

[Open the Streamlit App](YOUR_STREAMLIT_APP_URL)

## Author

Developed as an API integration and AI assistant project.
