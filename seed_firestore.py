# Copyright 2026 Google LLC
# Seed script for Apex Coach Firestore database

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-fcbe5502dab4"


def seed_database():
    print(f"Connecting to Firestore with hardcoded project ID: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)

    # 1. Seed workout_routines collection
    workouts = [
        {
            "id": "5k-beginner-runner",
            "name": "5K Beginner Base Builder",
            "category": "Running",
            "difficulty": "Beginner",
            "duration_mins": 30,
            "description": "Alternating intervals of light jogging and walking to build aerobic endurance safely.",
            "exercises": [
                "5 min warm-up walk",
                "6 x (2 min jog / 1 min walk)",
                "5 min cool-down walk",
                "Light quad & calf stretching",
            ],
        },
        {
            "id": "tempo-run-intermediate",
            "name": "10K Lactate Threshold Tempo",
            "category": "Running",
            "difficulty": "Intermediate",
            "duration_mins": 45,
            "description": "Sustained tempo run at comfortably hard pace to raise lactate threshold for 10K racing.",
            "exercises": [
                "10 min easy warm-up jog",
                "20 min sustained tempo run @ 80-85% HR max",
                "10 min cool-down jog",
                "Dynamic foam rolling",
            ],
        },
        {
            "id": "full-body-strength",
            "name": "Runner's Core & Leg Stability",
            "category": "Strength",
            "difficulty": "Beginner",
            "duration_mins": 40,
            "description": "Targeted bodyweight and dumbbell resistance training to improve single-leg balance and core strength.",
            "exercises": [
                "3 x 12 Single-leg Bulgarian Split Squats",
                "3 x 15 Swiss Ball Hamstring Curls",
                "3 x 45s Plank with Hip Dips",
                "3 x 12 Dumbbell Step-ups",
            ],
        },
        {
            "id": "recovery-mobility",
            "name": "Post-Long Run Active Mobility",
            "category": "Mobility",
            "difficulty": "All Levels",
            "duration_mins": 25,
            "description": "Gentle mobility flows targeting hips, hamstrings, and thoracic spine for accelerated post-workout recovery.",
            "exercises": [
                "90/90 Hip Swivels (2 mins)",
                "World's Greatest Stretch (8 per side)",
                "Pigeon Pose Hold (90s per side)",
                "Cat-Cow Spine Lubrication (10 reps)",
            ],
        },
    ]

    print("Seeding 'workout_routines' collection...")
    for workout in workouts:
        doc_id = workout["id"]
        db.collection("workout_routines").document(doc_id).set(workout)
        print(f"  - Added workout routine: {workout['name']} ({doc_id})")

    # 2. Seed gear_catalog collection
    gear_items = [
        {
            "id": "nike-pegasus-41",
            "name": "Nike Air Zoom Pegasus 41",
            "category": "Footwear",
            "brand": "Nike",
            "price": 140.0,
            "description": "Versatile daily trainer with responsive ReactX foam cushioning and dual Air Zoom units.",
            "specs": {
                "weight_oz": 10.4,
                "drop_mm": 10,
                "cushioning": "Medium",
                "terrain": "Road",
            },
        },
        {
            "id": "hoka-clifton-9",
            "name": "Hoka Clifton 9",
            "category": "Footwear",
            "brand": "Hoka",
            "price": 145.0,
            "description": "Lightweight max-cushion daily trainer for long recovery runs and smooth strides.",
            "specs": {
                "weight_oz": 8.7,
                "drop_mm": 5,
                "cushioning": "Max plush",
                "terrain": "Road/Track",
            },
        },
        {
            "id": "garmin-forerunner-265",
            "name": "Garmin Forerunner 265",
            "category": "Electronics",
            "brand": "Garmin",
            "price": 449.99,
            "description": "GPS running smartwatch with vivid AMOLED touchscreen display and advanced training readiness metrics.",
            "specs": {
                "battery_days": 13,
                "display": "1.3 inch AMOLED",
                "sensors": ["Optical HR", "GPS/GLONASS/Galileo", "Pulse Ox"],
            },
        },
        {
            "id": "salomon-active-skin-8",
            "name": "Salomon Active Skin 8 Hydration Vest",
            "category": "Accessories",
            "brand": "Salomon",
            "price": 115.0,
            "description": "Snug, breathable hydration vest with dual 500ml soft flasks included for trail and long distance runs.",
            "specs": {
                "volume_liters": 8.0,
                "flask_included": True,
                "pockets": 5,
            },
        },
    ]

    print("Seeding 'gear_catalog' collection...")
    for gear in gear_items:
        doc_id = gear["id"]
        db.collection("gear_catalog").document(doc_id).set(gear)
        print(f"  - Added gear item: {gear['name']} ({doc_id})")

    print("\n✅ Firestore database successfully seeded!")


if __name__ == "__main__":
    seed_database()
