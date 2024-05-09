import os
import requests
import csv
from plexapi.server import PlexServer

# Radarr configuration
RADARR_URL = "YOUR_RADARR_URL"
RADARR_API_KEY = "YOUR_RADARR_API"

# Plex configuration
PLEX_URL = "YOUR_PLEX_URL"
PLEX_TOKEN = "YOUR_PLEX_TOKEN"

# Connect to Plex server
plex = PlexServer(PLEX_URL, PLEX_TOKEN)

# Get the Plex library section
library_name = "Films"  # Adjust to your Plex library name
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

# Identify unmatched Radarr movies with tags
unmatched_radarr_movies_with_tags = [
    item for item in radarr_movie_names_with_tags if item[0] not in plex_movie_names and item[1]
]

# CSV output path
csv_output_path = r"YOUR_OUTPUT_PATH"

# Create a CSV file and write unmatched Radarr movies with tags
os.makedirs(os.path.dirname(csv_output_path), exist_ok=True)  # Ensure the output directory exists

with open(csv_output_path, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Unmatched Radarr Movie", "Radarr Tags"])  # Header row

    # Write unmatched Radarr movies with tags to the CSV file
    for movie, tags in unmatched_radarr_movies_with_tags:
        writer.writerow([movie, tags])

print(f"CSV file created at: {csv_output_path} with unmatched Radarr movies that have tags.")
