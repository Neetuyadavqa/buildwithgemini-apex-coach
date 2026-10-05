# Copyright 2026 Google LLC
# Firestore tools for Apex Coach

import json
from google.cloud import firestore

# CRITICAL: Hardcode the project ID string so it works both locally and deployed on Agent Platform!
PROJECT_ID = "qwiklabs-gcp-03-fcbe5502dab4"

# Initialize Firestore client with hardcoded project ID
db = firestore.Client(project=PROJECT_ID)


def search_workout_routines(category: str = "", difficulty: str = "") -> str:
    """Searches the Firestore database for workout routines matching category or difficulty.

    Args:
        category: Optional category filter (e.g. 'Running', 'Strength', 'Mobility').
        difficulty: Optional difficulty level filter (e.g. 'Beginner', 'Intermediate', 'Advanced').

    Returns:
        A JSON string containing the matching workout routines.
    """
    query = db.collection("workout_routines")
    if category:
        query = query.where("category", "==", category)
    if difficulty:
        query = query.where("difficulty", "==", difficulty)

    docs = query.stream()
    results = [doc.to_dict() for doc in docs]
    if not results:
        # Fallback to returning all routines if specific filters don't match
        all_docs = db.collection("workout_routines").stream()
        results = [d.to_dict() for d in all_docs]

    return json.dumps(results, indent=2)


def get_workout_routine_details(routine_id: str) -> str:
    """Retrieves full details for a specific workout routine by ID.

    Args:
        routine_id: The document ID of the workout routine (e.g. '5k-beginner-runner').

    Returns:
        A JSON string with workout routine details, or an error message if not found.
    """
    doc_ref = db.collection("workout_routines").document(routine_id)
    doc = doc_ref.get()
    if doc.exists:
        return json.dumps(doc.to_dict(), indent=2)
    return json.dumps({"error": f"Workout routine '{routine_id}' not found."})


def add_workout_routine(
    routine_id: str,
    name: str,
    category: str,
    difficulty: str,
    duration_mins: int,
    description: str,
    exercises: list[str],
) -> str:
    """Adds or updates a workout routine in the Firestore database.

    Args:
        routine_id: Unique slug identifier for the routine (e.g. 'marathon-long-run').
        name: Display name of the workout routine.
        category: Category (e.g. 'Running', 'Strength', 'Cross-Training').
        difficulty: Difficulty level (e.g. 'Beginner', 'Intermediate', 'Advanced').
        duration_mins: Total workout duration in minutes.
        description: Brief overview of the routine's focus and benefit.
        exercises: List of exercise steps or interval instructions.

    Returns:
        A JSON status message confirming the document creation.
    """
    routine_data = {
        "id": routine_id,
        "name": name,
        "category": category,
        "difficulty": difficulty,
        "duration_mins": duration_mins,
        "description": description,
        "exercises": exercises,
    }
    db.collection("workout_routines").document(routine_id).set(routine_data)
    return json.dumps({"status": "success", "message": f"Added workout routine '{name}' ({routine_id})."})


def search_gear_catalog(category: str = "", brand: str = "") -> str:
    """Searches the Firestore gear catalog for sports gear and footwear.

    Args:
        category: Optional category filter (e.g. 'Footwear', 'Electronics', 'Accessories').
        brand: Optional brand name filter (e.g. 'Nike', 'Hoka', 'Garmin', 'Salomon').

    Returns:
        A JSON string containing matching gear items.
    """
    query = db.collection("gear_catalog")
    if category:
        query = query.where("category", "==", category)
    if brand:
        query = query.where("brand", "==", brand)

    docs = query.stream()
    results = [doc.to_dict() for doc in docs]
    if not results:
        all_docs = db.collection("gear_catalog").stream()
        results = [d.to_dict() for d in all_docs]

    return json.dumps(results, indent=2)


def add_gear_item(
    item_id: str,
    name: str,
    category: str,
    brand: str,
    price: float,
    description: str,
    specs: dict | None = None,
) -> str:
    """Adds a new gear or footwear item to the Firestore gear catalog.

    Args:
        item_id: Unique slug identifier for the gear item (e.g. 'brooks-ghost-16').
        name: Full product name.
        category: Gear category (e.g. 'Footwear', 'Electronics', 'Apparel').
        brand: Manufacturer or brand name.
        price: Retail price in USD.
        description: Product description and suitability.
        specs: Optional dictionary of technical specifications.

    Returns:
        A JSON status message confirming creation.
    """
    gear_data = {
        "id": item_id,
        "name": name,
        "category": category,
        "brand": brand,
        "price": price,
        "description": description,
        "specs": specs or {},
    }
    db.collection("gear_catalog").document(item_id).set(gear_data)
    return json.dumps({"status": "success", "message": f"Added gear item '{name}' ({item_id})."})


def calculate_training_zones_and_pace(
    race_distance_km: float, race_time_mins: float, max_hr: int = 185
) -> str:
    """Calculates personalized running pace targets and Heart Rate Zones.

    Args:
        race_distance_km: Distance of a recent race or time trial in kilometers (e.g., 5.0 for 5K, 10.0 for 10K).
        race_time_mins: Total finish time in minutes (e.g., 25.0).
        max_hr: Maximum heart rate in BPM (defaults to 185 if unknown).

    Returns:
        A JSON string containing calculated training paces (Easy, Tempo, Interval) and Heart Rate Zones (Z1-Z5).
    """
    if race_distance_km <= 0 or race_time_mins <= 0:
        return json.dumps({"error": "Distance and time must be positive numbers."})

    base_pace = race_time_mins / race_distance_km  # mins per km

    def fmt_pace(p_mins: float) -> str:
        mins = int(p_mins)
        secs = int(round((p_mins - mins) * 60))
        if secs == 60:
            mins += 1
            secs = 0
        return f"{mins}:{secs:02d} /km"

    easy_pace = base_pace * 1.25
    tempo_pace = base_pace * 1.08
    interval_pace = base_pace * 0.95

    hr_zones = {
        "Zone 1 (Recovery / Warm-up)": f"{int(max_hr * 0.50)}-{int(max_hr * 0.60)} bpm",
        "Zone 2 (Aerobic Base / Long Run)": f"{int(max_hr * 0.60)}-{int(max_hr * 0.70)} bpm",
        "Zone 3 (Tempo / Moderate)": f"{int(max_hr * 0.70)}-{int(max_hr * 0.80)} bpm",
        "Zone 4 (Threshold / Hard)": f"{int(max_hr * 0.80)}-{int(max_hr * 0.90)} bpm",
        "Zone 5 (Anaerobic / Max Effort)": f"{int(max_hr * 0.90)}-{max_hr} bpm",
    }

    results = {
        "recent_performance": {
            "distance_km": race_distance_km,
            "time_mins": race_time_mins,
            "race_pace": fmt_pace(base_pace),
        },
        "target_training_paces": {
            "easy_long_run_pace": fmt_pace(easy_pace),
            "tempo_threshold_pace": fmt_pace(tempo_pace),
            "interval_speed_pace": fmt_pace(interval_pace),
        },
        "heart_rate_zones": hr_zones,
    }

    return json.dumps(results, indent=2)

