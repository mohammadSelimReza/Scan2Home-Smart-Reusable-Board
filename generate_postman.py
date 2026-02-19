import json
import urllib.request
import re

OPENAPI_URL = "http://localhost:8000/api/schema/?format=json"
OUTPUT_FILE = "Scan2Home_Postman_Collection.json"

def fetch_openapi():
    print(f"Fetching OpenAPI schema from {OPENAPI_URL}...")
    try:
        with urllib.request.urlopen(OPENAPI_URL) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching schema: {e}")
        return None

def create_item(name, method, url, desc, body=None, query_params=None):
    item = {
        "name": name,
        "request": {
            "method": method.upper(),
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": {
                "raw": "{{baseUrl}}" + url,
                "host": ["{{baseUrl}}"],
                "path": url.strip("/").split("/"),
                "query": query_params or []
            },
            "description": desc or ""
        },
        "response": []
    }
    if body:
        item["request"]["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=2)
        }
    return item

def get_ref_schema(schema_ref, components):
    # schema_ref: #/components/schemas/Name
    name = schema_ref.split("/")[-1]
    return components.get("schemas", {}).get(name, {})

def resolve_schema(schema, components):
    if "$ref" in schema:
        return resolve_schema(get_ref_schema(schema["$ref"], components), components)
    if "allOf" in schema:
        combined = {}
        for sub in schema["allOf"]:
            combined.update(resolve_schema(sub, components))
        return combined
    return schema

def extract_body_example(content, components):
    # content: {'application/json': {'schema': ...}}
    if not content or "application/json" not in content:
        return None
    
    schema = content["application/json"]["schema"]
    resolved = resolve_schema(schema, components)
    
    example = {}
    properties = resolved.get("properties", {})
    for prop, details in properties.items():
        if "example" in details:
            example[prop] = details["example"]
        else:
            typ = details.get("type")
            if typ == "string": example[prop] = "string"
            elif typ == "integer": example[prop] = 0
            elif typ == "boolean": example[prop] = True
            elif typ == "array": example[prop] = []
            elif typ == "object": example[prop] = {}
    return example

def main():
    schema = fetch_openapi()
    if not schema:
        return

    collection = {
        "info": {
            "name": "Scan2Home API",
            "description": "Collection generated from OpenAPI schema, grouped by Role.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": [
            {"name": "Admin", "item": []},
            {"name": "Agent", "item": []},
            {"name": "User", "item": []}
        ],
        "variable": [
            {"key": "baseUrl", "value": "http://localhost:8000", "type": "string"}
        ]
    }

    folders = {
        "Admin": collection["item"][0]["item"],
        "Agent": collection["item"][1]["item"],
        "User": collection["item"][2]["item"],
    }

    paths = schema.get("paths", {})
    components = schema.get("components", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            operation_id = details.get("operationId", "")
            summary = details.get("summary", operation_id)
            desc = details.get("description", "")
            tags = details.get("tags", [])
            
            # Extract Body
            body_example = None
            if "requestBody" in details:
                body_example = extract_body_example(details["requestBody"].get("content"), components)

            # Extract Query Params
            q_params = []
            if "parameters" in details:
                for param in details["parameters"]:
                    if param.get("in") == "query":
                        q_params.append({
                            "key": param["name"],
                            "value": "",
                            "description": param.get("description", "")
                        })

            item = create_item(summary, method, path, desc, body_example, q_params)

            # --- ROUTING LOGIC ---
            
            # 1. ADMIN
            if path.startswith("/api/v1/admin") or "Admin" in tags:
                folders["Admin"].append(item)
                continue

            # 2. SHARED AUTH (Duplicate to User and Agent)
            if path.startswith("/api/v1/auth"):
                if "register/buyer" in path:
                    folders["User"].append(item)
                elif "register/agent" in path:
                    folders["Agent"].append(item)
                else:
                    # Login, Password, etc -> Both
                    import copy
                    folders["User"].append(copy.deepcopy(item))
                    folders["Agent"].append(copy.deepcopy(item))
                continue

            # 3. AGENT SPECIFIC
            if "QR Boards" in tags or "Agent" in tags or "/agent" in path or method in ["patch", "delete", "put"]:
                # Check for public exceptions
                if "scan-redirect" in path: 
                    folders["User"].append(item) # QR Scan is Public
                else:
                    folders["Agent"].append(item)
            
            # 4. PROPERTIES & OFFERS (Mixed)
            elif "Properties" in tags:
                if method == "post": # Create
                    folders["Agent"].append(item)
                else: # List/Get
                    folders["User"].append(item)
                    # Agents also need to see properties, maybe duplicate?
                    import copy
                    folders["Agent"].append(copy.deepcopy(item))

            elif "Offers" in tags:
                if method == "post" and "submit" in path: # User submitting offer? No, path is /offers/ usually
                    # Check operation ID or description?
                    # SubmitOfferView -> post
                    folders["User"].append(item)
                else:
                    folders["Agent"].append(item) # Agent viewing/managing offers

            elif "Bookings" in tags:
                if method == "post": # Create booking
                    folders["User"].append(item)
                else:
                    folders["User"].append(item) # My bookings
                    import copy
                    folders["Agent"].append(copy.deepcopy(item)) # Agent bookings
            
            elif "Chat" in tags:
                folders["User"].append(item)
            
            elif "Notifications" in tags:
                folders["User"].append(item)
                import copy
                folders["Agent"].append(copy.deepcopy(item))
            
            else:
                # Default to User
                folders["User"].append(item)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(collection, f, indent=2)
    
    print(f"Successfully generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
