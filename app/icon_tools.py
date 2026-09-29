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

"""Icon tools calling the free open-source Iconify API for diagram vector assets."""

import json
import urllib.parse
import urllib.request


def search_vector_icons(query: str, limit: int = 5) -> str:
    """Searches the open-source Iconify API for SVG vector icons and graphics.

    Use this tool to find real SVG icon identifiers (e.g., 'mdi:database', 'carbon:cloud')
    for diagram components, cloud resources, servers, and tech architecture symbols.

    Args:
        query: Search term for the diagram block or icon (e.g. 'database', 'server', 'kubernetes', 'cloud').
        limit: Maximum number of icons to return (default 5, max 20).

    Returns:
        JSON string containing matching icon names, collections, and preview SVG URLs.
    """
    try:
        clean_query = query.strip()
        limit_val = max(1, min(limit, 20))
        encoded_query = urllib.parse.quote(clean_query)
        search_url = f"https://api.iconify.design/search?query={encoded_query}&limit={limit_val}"

        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "DiagramDecon-Agent/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            if response.status != 200:
                return json.dumps({
                    "status": "error",
                    "message": f"Iconify API returned HTTP {response.status}"
                })
            payload = json.loads(response.read().decode("utf-8"))

        icons = payload.get("icons", [])
        results = []
        for icon in icons[:limit_val]:
            parts = icon.split(":", 1)
            prefix = parts[0]
            name = parts[1] if len(parts) > 1 else parts[0]
            svg_url = f"https://api.iconify.design/{prefix}/{name}.svg"
            results.append({
                "icon_id": icon,
                "prefix": prefix,
                "name": name,
                "svg_url": svg_url
            })

        return json.dumps({
            "status": "success",
            "query": clean_query,
            "count": len(results),
            "icons": results
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Failed to search vector icons: {str(e)}"
        })
