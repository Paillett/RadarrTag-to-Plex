import requests
from plexapi.server import PlexServer
from plexapi.exceptions import NotFound

# Radarr configuration
RADARR_URL = "YOUR_RADARR_URL"
RADARR_API_KEY = "YOUR_RADARR_API"

# Plex configuration
PLEX_URL = "YOUR_PLEX_URL"
PLEX_TOKEN = "YOUR_PLEX_TOKEN"

# Connect to Plex server
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Get the Plex library section
library_name = "YOUR_LIBRARY_NAME"  # Adjust to your Plex library name
plex_library = plex.library.section(library_name)

# Fetch all movies from Radarr
radarr_response = requests.get(
    f"{RADARR_URL}/api/v3/movie",
    headers={"X-Api-Key": RADARR_API_KEY}
)

if radarr_response.status_code != 200:
    raise Exception(f"Failed to retrieve data from Radarr. Status code: {radarr_response.status_code}")

radarr_movies = radarr_response.json()

# Fetch Radarr tags to map tag IDs to tag names
tags_response = requests.get(
    f"{RADARR_URL}/api/v3/tag",
    headers={"X-Api-Key": RADARR_API_KEY}
)

if tags_response.status_code != 200:
    raise Exception(f"Failed to fetch Radarr tags. Status code: {tags_response.status_code}")

radarr_tags = {tag["id"]: tag["label"] for tag in tags_response.json()}

# Get Radarr movie names with tags
radarr_movie_names_with_tags = {
    (movie["title"].lower(), ", ".join(radarr_tags[tag_id] for tag_id in movie.get("tags", [])))
    for movie in radarr_movies
}

# Get Plex movie names
plex_movie_names = {movie.title.lower() for movie in plex_library.all()}

# Create a comprehensive set of all unique movie names (lowercase for case-insensitive matching)
all_movie_names = {name[0] for name in radarr_movie_names_with_tags}.union(plex_movie_names)

# Dictionary to store Plex collections
collections = {}

# Create Plex collections based on Radarr tags and add movies to them
for name in sorted(all_movie_names):
    radarr_match = next((item for item in radarr_movie_names_with_tags if item[0] == name), ("", ""))
    plex_match = name if name in plex_movie_names else ""

    # Check if there's a match and if the Plex movie exists
    if radarr_match[0] and plex_match:
        # Ensure Radarr tags are not None or empty
        radarr_tags = radarr_match[1] if radarr_match[1] else ""

        # Create collections based on Radarr tags
        if radarr_tags:
            tags = radarr_tags.split(", ")
        else:
            tags = []

        try:
            plex_movie_object = plex_library.get(plex_match)

            # Create collections based on Radarr tags and add movies
            for tag in tags:
                collection_name = tag  # Collection name without "Radarr Tag: "

                if collection_name not in collections:
                    # Create the collection with the first item
                    collections[collection_name] = plex_library.createCollection(collection_name, items=[plex_movie_object])
                else:
                    # Add movies to the existing collection
                    collections[collection_name].addItems([plex_movie_object])

        except NotFound:
            print(f"Movie '{plex_match}' not found in Plex.")

        except Exception as e:
            print(f"Error adding movie '{plex_match}' to collection: {e}")

print("Plex collections created based on Radarr tags for matched movies.")
