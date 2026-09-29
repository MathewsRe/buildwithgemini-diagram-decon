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

"""Image generation tools for diagram visual concepts and raster reference assets."""

import json
import uuid
from typing import Optional
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

GCP_PROJECT_ID = "qwiklabs-gcp-03-2e4c275e4ad8"
BUCKET_NAME = "diagram-decon-svg-assets-qwiklabs-gcp-03-2e4c275e4ad8"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
IMAGE_LOCATION = "global"

_genai_client: Optional[genai.Client] = None
_storage_client: Optional[storage.Client] = None


def get_genai_client() -> genai.Client:
    """Returns a client configured for Vertex AI image generation in the global region."""
    global _genai_client
    if _genai_client is None:
        _genai_client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location=IMAGE_LOCATION,
        )
    return _genai_client


def get_storage_client() -> storage.Client:
    """Returns a singleton Cloud Storage client."""
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=GCP_PROJECT_ID)
    return _storage_client


async def generate_diagram_image(
    prompt: str,
    tool_context: ToolContext,
    filename: Optional[str] = None,
) -> str:
    """Generates a diagram visual asset using gemini-3.1-flash-lite-image.

    Saves the image as a session artifact and uploads it to public Cloud Storage.

    Args:
        prompt: Visual prompt describing the diagram, architecture concept, or component.
        tool_context: ToolContext provided by ADK runtime for session artifacts.
        filename: Optional filename (e.g. 'architecture_concept.png'). If omitted, one is generated.

    Returns:
        JSON string containing publication status, public URL, and artifact details.
    """
    try:
        # 1. Determine destination object name
        if filename and filename.strip():
            clean_name = filename.strip().lstrip("/")
            if not (clean_name.endswith(".png") or clean_name.endswith(".jpg") or clean_name.endswith(".jpeg")):
                clean_name += ".png"
        else:
            clean_name = f"diagram_concept_{uuid.uuid4().hex[:8]}.png"

        # 2. Call gemini-3.1-flash-lite-image in global region
        client = get_genai_client()
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"],
            ),
        )

        image_bytes: Optional[bytes] = None
        mime_type = "image/png"

        for part in response.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/png"
                break

        if not image_bytes:
            return json.dumps({
                "status": "error",
                "message": "No image data returned from image generation model."
            })

        # 3. Save as session artifact via tool_context
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        artifact_version = None
        try:
            artifact_version = await tool_context.save_artifact(
                filename=clean_name,
                artifact=artifact_part,
            )
        except Exception as e:
            # Continue even if session artifact service is unconfigured
            pass

        # 4. Upload raw bytes to public Cloud Storage
        storage_client = get_storage_client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(clean_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{clean_name}"

        return json.dumps({
            "status": "success",
            "message": f"Successfully generated and published diagram image as '{clean_name}'.",
            "filename": clean_name,
            "artifact_version": artifact_version,
            "public_url": public_url,
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to generate diagram image: {str(e)}"
        })
