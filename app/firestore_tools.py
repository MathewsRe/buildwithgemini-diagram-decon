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

"""Firestore tools for DiagramDecon block and component catalog."""

import json
from typing import Any, Dict, List, Optional
from google.cloud import firestore

# Hardcoded Project ID string to prevent Agent Platform project number resolution issues
GCP_PROJECT_ID = "qwiklabs-gcp-03-2e4c275e4ad8"
COLLECTION_NAME = "diagram_blocks"

_db_client: Optional[firestore.Client] = None


def get_firestore_client() -> firestore.Client:
    """Returns a singleton Firestore client instance configured with the explicit project ID."""
    global _db_client
    if _db_client is None:
        _db_client = firestore.Client(project=GCP_PROJECT_ID)
    return _db_client


def _json_serialize(obj: Any) -> Any:
    """Helper serializer for Firestore timestamps and special types."""
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    return str(obj)


def list_diagram_blocks(category: Optional[str] = None) -> str:
    """Lists reusable SVG diagram blocks and components stored in Firestore.

    Args:
        category: Optional filter by category (e.g. 'compute', 'storage', 'database', 'network', 'gateway').

    Returns:
        JSON string representing the list of diagram blocks and their SVG specifications.
    """
    try:
        db = get_firestore_client()
        query = db.collection(COLLECTION_NAME)
        if category:
            query = query.where("category", "==", category.strip().lower())

        docs = query.stream()
        results: List[Dict[str, Any]] = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            results.append(data)

        return json.dumps({"status": "success", "count": len(results), "blocks": results}, indent=2, default=_json_serialize)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to list diagram blocks: {str(e)}"})


def get_diagram_block(block_id: str) -> str:
    """Retrieves the details and SVG template code for a specific diagram block by ID.

    Args:
        block_id: Unique identifier for the diagram block (e.g. 'api-gateway', 'cloud-storage').

    Returns:
        JSON string containing the block metadata and SVG template.
    """
    try:
        db = get_firestore_client()
        doc_ref = db.collection(COLLECTION_NAME).document(block_id.strip())
        doc = doc_ref.get()

        if not doc.exists:
            return json.dumps({"status": "error", "message": f"Diagram block '{block_id}' not found."})

        data = doc.to_dict()
        data["id"] = doc.id
        return json.dumps({"status": "success", "block": data}, indent=2, default=_json_serialize)
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to get diagram block: {str(e)}"})


def save_diagram_block(
    block_id: str,
    name: str,
    category: str,
    svg_code: str,
    width: int = 160,
    height: int = 80,
    tags: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> str:
    """Creates or updates an SVG diagram block in Firestore.

    Args:
        block_id: Unique document ID / slug (e.g., 'event-queue', 'auth-service').
        name: Human-readable name for the block.
        category: Category (e.g. 'compute', 'storage', 'database', 'network', 'messaging').
        svg_code: Raw SVG code representing this block.
        width: Default pixel width of the block.
        height: Default pixel height of the block.
        tags: List of descriptive keyword tags.
        description: Brief description of what this block represents in system architecture.

    Returns:
        JSON string indicating operation outcome.
    """
    try:
        db = get_firestore_client()
        data = {
            "name": name,
            "category": category.strip().lower(),
            "svg_code": svg_code,
            "width": width,
            "height": height,
            "tags": tags or [],
            "description": description or "",
            "updated_at": firestore.SERVER_TIMESTAMP,
        }
        db.collection(COLLECTION_NAME).document(block_id.strip()).set(data, merge=True)
        return json.dumps({"status": "success", "message": f"Block '{name}' ({block_id}) saved successfully."})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"Failed to save diagram block: {str(e)}"})
