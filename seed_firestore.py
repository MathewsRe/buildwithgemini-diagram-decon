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

"""Seed script to populate Firestore with initial diagram block templates for DiagramDecon."""

import sys
from google.cloud import firestore

# Hardcoded Project ID string to ensure correct project binding
GCP_PROJECT_ID = "qwiklabs-gcp-03-2e4c275e4ad8"
COLLECTION_NAME = "diagram_blocks"

SAMPLE_BLOCKS = [
    {
        "id": "api-gateway",
        "name": "API Gateway",
        "category": "gateway",
        "description": "Ingress router and API management endpoint for incoming client traffic.",
        "width": 180,
        "height": 90,
        "tags": ["gateway", "ingress", "router", "http"],
        "svg_code": """<svg width="180" height="90" viewBox="0 0 180 90" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="176" height="86" rx="8" fill="#E8F0FE" stroke="#4285F4" stroke-width="2" />
  <circle cx="28" cy="45" r="16" fill="#4285F4"/>
  <text x="28" y="50" font-family="sans-serif" font-size="12" fill="#FFFFFF" text-anchor="middle" font-weight="bold">&gt;</text>
  <text x="56" y="42" font-family="sans-serif" font-size="14" font-weight="bold" fill="#202124">API Gateway</text>
  <text x="56" y="60" font-family="sans-serif" font-size="11" fill="#5F6368">Traffic Ingress</text>
</svg>""",
    },
    {
        "id": "cloud-run-service",
        "name": "Cloud Run Microservice",
        "category": "compute",
        "description": "Serverless container compute engine running core business logic.",
        "width": 190,
        "height": 90,
        "tags": ["compute", "serverless", "microservice", "container"],
        "svg_code": """<svg width="190" height="90" viewBox="0 0 190 90" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="186" height="86" rx="8" fill="#E6F4EA" stroke="#34A853" stroke-width="2" />
  <rect x="16" y="33" width="24" height="24" rx="4" fill="#34A853"/>
  <text x="52" y="42" font-family="sans-serif" font-size="14" font-weight="bold" fill="#202124">Cloud Run</text>
  <text x="52" y="60" font-family="sans-serif" font-size="11" fill="#5F6368">Backend Worker</text>
</svg>""",
    },
    {
        "id": "firestore-db",
        "name": "Firestore Document DB",
        "category": "database",
        "description": "NoSQL document database storing collections of records and block schemas.",
        "width": 190,
        "height": 90,
        "tags": ["database", "nosql", "firestore", "storage"],
        "svg_code": """<svg width="190" height="90" viewBox="0 0 190 90" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="186" height="86" rx="8" fill="#FEF7E0" stroke="#FBBC04" stroke-width="2" />
  <circle cx="28" cy="45" r="14" fill="#FBBC04"/>
  <text x="52" y="42" font-family="sans-serif" font-size="14" font-weight="bold" fill="#202124">Firestore</text>
  <text x="52" y="60" font-family="sans-serif" font-size="11" fill="#5F6368">Catalog & State DB</text>
</svg>""",
    },
    {
        "id": "cloud-storage-bucket",
        "name": "Cloud Storage Bucket",
        "category": "storage",
        "description": "Object storage bucket for vector SVG diagram files and exported bundles.",
        "width": 180,
        "height": 90,
        "tags": ["storage", "gcs", "blob", "svg"],
        "svg_code": """<svg width="180" height="90" viewBox="0 0 180 90" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="176" height="86" rx="8" fill="#FCE8E6" stroke="#EA4335" stroke-width="2" />
  <circle cx="28" cy="45" r="14" fill="#EA4335"/>
  <text x="52" y="42" font-family="sans-serif" font-size="14" font-weight="bold" fill="#202124">Cloud Storage</text>
  <text x="52" y="60" font-family="sans-serif" font-size="11" fill="#5F6368">SVG Asset Bucket</text>
</svg>""",
    },
    {
        "id": "pubsub-topic",
        "name": "Pub/Sub Event Bus",
        "category": "messaging",
        "description": "Asynchronous event messaging bus connecting diagram parsing tasks.",
        "width": 180,
        "height": 90,
        "tags": ["messaging", "pubsub", "queue", "events"],
        "svg_code": """<svg width="180" height="90" viewBox="0 0 180 90" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="2" width="176" height="86" rx="8" fill="#F3E8FD" stroke="#A142F4" stroke-width="2" />
  <circle cx="28" cy="45" r="14" fill="#A142F4"/>
  <text x="52" y="42" font-family="sans-serif" font-size="14" font-weight="bold" fill="#202124">Pub/Sub</text>
  <text x="52" y="60" font-family="sans-serif" font-size="11" fill="#5F6368">Decon Event Queue</text>
</svg>""",
    },
]


def seed_database():
    print(f"Connecting to Firestore in project '{GCP_PROJECT_ID}'...")
    db = firestore.Client(project=GCP_PROJECT_ID)
    collection = db.collection(COLLECTION_NAME)

    for item in SAMPLE_BLOCKS:
        doc_id = item.pop("id")
        item["created_at"] = firestore.SERVER_TIMESTAMP
        collection.document(doc_id).set(item, merge=True)
        print(f"  ✓ Seeded block: {doc_id} ('{item['name']}')")

    print(f"\nSuccessfully seeded {len(SAMPLE_BLOCKS)} items into collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    try:
        seed_database()
    except Exception as e:
        print(f"Error seeding database: {e}", file=sys.stderr)
        sys.exit(1)
