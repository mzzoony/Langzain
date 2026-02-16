# tools.py
import datetime
import requests
import wikipedia


def get_current_temperature(latitude: float, longitude: float) -> str:
    """
    Fetch the current temperature (approx.) for the given coordinates
    using the Open-Meteo API. Returns a human-readable sentence.
    """
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "forecast_days": 1,
    }

    resp = requests.get(BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current_utc = datetime.datetime.utcnow()
    times = [
        datetime.datetime.fromisoformat(t.replace("Z", "+00:00"))
        for t in data["hourly"]["time"]
    ]
    temps = data["hourly"]["temperature_2m"]

    idx = min(range(len(times)), key=lambda i: abs(times[i] - current_utc))
    temp = temps[idx]

    return f"The current temperature is {temp:.1f} °C."


def search_wikipedia(query: str) -> str:
    """
    Search Wikipedia and return summaries for up to 3 results.
    """
    titles = wikipedia.search(query)
    summaries = []
    for title in titles[:3]:
        try:
            page = wikipedia.page(title=title, auto_suggest=False)
            summaries.append(f"Page: {title}\nSummary: {page.summary}")
        except Exception:

            continue

    if not summaries:
        return "No good Wikipedia search result was found."
    return "\n\n".join(summaries)
