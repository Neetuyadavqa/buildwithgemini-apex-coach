# Apex Coach 🏃⚡

> **Conversational AI Athletic & Gear Coach** powered by Google Cloud's Agent Development Kit (ADK), Gemini 2.5 Flash, Vertex AI Memory Bank, Firestore, and A2UI.

![Apex Coach Demo](demo.gif)

---

## 🌟 Overview

**Apex Coach** is an intelligent, multimodal fitness and athletic assistant designed for runners, endurance athletes, and fitness enthusiasts. It provides personalized workout routines, tailored athletic gear recommendations, training pace and heart rate zone calculations, live outdoor running weather suitability, location geocoding, nearby venue search, custom AI image & video generation, and dynamic A2UI surface rendering.

---

## 🛠️ Implemented Architecture & Google Cloud Services

Apex Coach is built on **Google Cloud Platform** and the **Agent Development Kit (ADK)**. Based on the codebase in `app/` and `agents-cli-manifest.yaml`, the following services and tools are fully implemented and operational:

### 1. 🧠 Long-Term Personalization (Vertex AI Memory Bank)
- **Service**: `google.adk.memory.VertexAiMemoryBankService`
- **Capabilities**:
  - Automatically extracts and persists user preferences, fitness goals, health conditions, physical restrictions, and **allergies** across sessions.
  - Automatically checks remembered allergies before recommending workout nutrition, gear materials, or outdoor running locations.
  - Implements `PreloadMemoryTool` and an `after_agent_callback` (`generate_memories_callback`) for continuous memory extraction.

### 2. 🗄️ Firestore Database Integration
- **Service**: Google Cloud Firestore (`google-cloud-firestore`)
- **Implemented Tools**:
  - `search_workout_routines`: Queries Firestore for marathon, half-marathon, 5K, and strength routines filtered by experience level.
  - `get_workout_routine_details`: Retrieves detailed day-by-day training schedules.
  - `add_workout_routine`: Saves custom workout routines directly to Firestore.
  - `search_gear_catalog`: Searches running shoes, trail gear, electronics, and apparel by category.
  - `add_gear_item`: Adds new gear items and specifications to the Firestore catalog.
  - `calculate_training_zones_and_pace`: Calculates heart rate zones and target training paces (Easy, Tempo, Interval).

### 3. 🖼️ AI Image & Video Generation + Cloud Storage
- **Services**: Vertex AI Imagen 3, Vertex AI Omni Model, Google Cloud Storage (GCS)
- **Implemented Tools**:
  - `generate_fitness_image`: Generates high-resolution gear and athletic visuals using `imagen-3.0-generate-002`, saves artifacts, uploads bytes to a public Cloud Storage bucket, and returns public HTTPS URLs.
  - `generate_fitness_video`: Generates short fitness videos using `gemini-omni-flash-preview` via the Vertex AI Interactions API, saves Playground artifacts, and uploads MP4 bytes to a public GCS bucket.

### 4. 🎨 A2UI Dynamic Interface Rendering
- **Service**: `a2ui` (v0.8)
- **Capabilities**:
  - Uses `A2uiSchemaManager` with the `BasicCatalog` configuration and `a2ui_callback` to generate structured JSON UI components (Cards, Columns, Rows, Text, Images).
  - Renders inline interactive workout cards, exercise breakdowns, and gear previews directly in the chat UI.

### 5. 📍 Google Maps Platform & Outdoor Weather
- **Services**: Google Maps Geocoding API, Places API, Open-Meteo Weather API
- **Implemented Tools**:
  - `geocode_address`: Converts addresses and venue names into geographic coordinates.
  - `find_nearby_places`: Finds nearby parks, outdoor tracks, gyms, and running venues.
  - `get_live_outdoor_weather`: Retrieves real-time weather forecasts and evaluates outdoor running suitability.

### 6. 🧪 Code Execution Sandbox
- **Service**: `AgentEngineSandboxCodeExecutor`
- **Capabilities**:
  - Executes Python code in a secure sandbox environment for complex fitness or race prediction math.

---

## 📋 Planned / Not Yet Implemented Features

The following items from `project_brief.md` are planned for future releases:
- **Production Observability**: Cloud Trace & BigQuery Agent Analytics integration *(Planned)*.
- **Wearable Device Sync**: Direct API integration with smartwatch telemetry *(Planned)*.

---

## 🚀 Setup & Local Execution Guide

Follow these instructions to run the Apex Coach backend agent and frontend locally.

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Authenticated `gcloud` CLI with access to your GCP project

### 1. Backend Agent Setup
1. Clone the repository and navigate to the root directory:
   ```bash
   cd apex-coach
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/us-central1/reasoningEngines/<RESOURCE_ID>"
   export AGENT_DIRECTORY="app"
   ```
4. Start the backend server:
   ```bash
   python main.py
   ```

### 2. Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the frontend development server:
   ```bash
   npm start
   ```

---

## 📄 License
Licensed under the [Apache License, Version 2.0](LICENSE).
