# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.external_tools import get_live_outdoor_weather
from app.firestore_tools import (
    add_gear_item,
    add_workout_routine,
    calculate_training_zones_and_pace,
    get_workout_routine_details,
    search_gear_catalog,
    search_workout_routines,
)
from app.image_tools import generate_fitness_image, generate_fitness_video
from app.maps_tools import find_nearby_places, geocode_address

# Load Agent Engine resource name from deployment_metadata.json if available
_metadata_path = Path(__file__).parent.parent / "deployment_metadata.json"
_agent_engine_resource_name = None
if _metadata_path.exists():
    try:
        _metadata = json.loads(_metadata_path.read_text())
        _agent_engine_resource_name = _metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=_agent_engine_resource_name
)

# Set memory service in app code for deployment
_memory_bank_id = (
    _agent_engine_resource_name.split("/")[-1]
    if _agent_engine_resource_name
    else "7782501081317113856"
)


def memory_service_builder():
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-03-fcbe5502dab4",
        location="us-central1",
        agent_engine_id=_memory_bank_id,
    )


memory_service = memory_service_builder()


async def generate_memories_callback(callback_context: CallbackContext):
    """WRITE: After each turn, send the session to Memory Bank for fact extraction."""
    try:
        await callback_context.add_session_to_memory()
    except ValueError:
        pass
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it to get information on weather for outdoor runs.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

apex_coach_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Apex Coach, an expert fitness & athletic gear AI assistant.\n\n"
        "Your primary mission is to help athletes, runners, and fitness enthusiasts find workout routines, get tailored gear recommendations, calculate training paces/zones, check live outdoor running weather, geocode locations, find nearby parks/gyms/running spots, generate custom motivational or gear images, and run endurance/fitness calculation scripts in a secure sandbox.\n\n"
        "Memory & Personalization (Allergies & Health Restrictions):\n"
        "- You remember user facts, preferences, health conditions, and ALLERGIES across sessions.\n"
        "- Pay special attention to all user allergies (e.g., food/nutrition allergies, pollen/environmental allergens for outdoor runs, medication allergies, or fabric/material sensitivities like latex, neoprene, synthetic dyes, or metals in athletic wear and wearables).\n"
        "- When a user states an allergy, acknowledge it and ensure it is remembered.\n"
        "- Always check and respect all recalled user allergies before recommending workout routines, nutrition, gear, or outdoor running locations.\n\n"
        "Capabilities:\n"
        "1. Search and inspect workout routines in Firestore using `search_workout_routines` and `get_workout_routine_details`.\n"
        "2. Add new workout routines to Firestore using `add_workout_routine`.\n"
        "3. Search and recommend running shoes, electronics, and athletic gear using `search_gear_catalog`.\n"
        "4. Add new gear items to the Firestore catalog using `add_gear_item`.\n"
        "5. Calculate target training paces (Easy, Tempo, Interval) and Heart Rate Zones using `calculate_training_zones_and_pace`.\n"
        "6. Check live weather forecast and outdoor running suitability using `get_live_outdoor_weather`.\n"
        "7. Geocode addresses and location names using `geocode_address`.\n"
        "8. Search for nearby parks, gyms, and athletic venues using `find_nearby_places`.\n"
        "9. Generate custom imagery for gear, athletic items, or workout scenes using `generate_fitness_image`.\n"
        "10. Generate short videos for athletic gear, workout demonstrations, or athletic scenes using `generate_fitness_video`.\n"
        "11. Execute Python code in a secure sandbox environment for complex fitness or endurance calculations.\n\n"
        "Always be encouraging, precise, and structured in your athletic advice!"
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=apex_coach_instruction,
    tools=[
        get_weather,
        get_current_time,
        search_workout_routines,
        get_workout_routine_details,
        add_workout_routine,
        search_gear_catalog,
        add_gear_item,
        calculate_training_zones_and_pace,
        get_live_outdoor_weather,
        geocode_address,
        find_nearby_places,
        generate_fitness_image,
        generate_fitness_video,
        PreloadMemoryTool(),
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
    code_executor=code_executor,
)

app = App(
    root_agent=root_agent,
    name="app",
)
