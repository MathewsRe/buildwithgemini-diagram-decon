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

"""Cloud Storage tools for publishing and serving SVG diagram assets."""

import json
import xml.etree.ElementTree as ET
from typing import Optional
from google.cloud import storage

GCP_PROJECT_ID = "qwiklabs-gcp-03-2e4c275e4ad8"
BUCKET_NAME = f"diagram-decon-svg-assets-{GCP_PROJECT_ID}"

_storage_client: Optional[storage.Client] = None


def get_storage_client() -> storage.Client:
    """Returns a singleton Cloud Storage client instance."""
    global _storage_client
    if _storage_client is None:
        _storage_client = storage.Client(project=GCP_PROJECT_ID)
    return _storage_client


def publish_svg_to_gcs(filename: str, svg_code: str) -> str:
    """Validates and uploads an SVG diagram to the public Cloud Storage bucket.

    Args:
        filename: Destination filename or path within the bucket (e.g. 'architecture.svg' or 'blocks/gateway.svg').
        svg_code: Complete raw SVG XML markup string.

    Returns:
        JSON string containing publication status, public URL, and GCS URI.
    """
    try:
        # 1. Clean filename
        clean_name = filename.strip().lstrip("/")
        if not clean_name.endswith(".svg"):
            clean_name += ".svg"

        # 2. Basic XML validation
        try:
            ET.fromstring(svg_code.strip())
        except ET.ParseError as pe:
            return json.dumps({
                "status": "error",
                "message": f"Invalid SVG XML markup: {str(pe)}"
            })

        # 3. Upload to Cloud Storage
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(clean_name)
        blob.upload_from_string(svg_code.strip(), content_type="image/svg+xml")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{clean_name}"
        gcs_uri = f"gs://{BUCKET_NAME}/{clean_name}"

        return json.dumps({
            "status": "success",
            "message": f"Successfully published SVG to Cloud Storage as '{clean_name}'.",
            "filename": clean_name,
            "public_url": public_url,
            "gcs_uri": gcs_uri
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to publish SVG: {str(e)}"
        })
