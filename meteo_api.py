
import sys
import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


def trouver_ville(nom: str) -> dict:
    """Convertit un nom de ville en coordonnées GPS."""
    r = requests.get(
        GEOCODING_URL,
        params={"name": nom, "count": 1, "language": "fr"},
        timeout=10,
    )
    r.raise_for_status()
    resultats = r.json().get("results")
    if not resultats:
        raise ValueError(f"Ville introuvable : {nom}")
    return resultats[0]


def obtenir_meteo(lat: float, lon: float) -> dict:
    """Récupère la météo actuelle et les prévisions sur 3 jours."""
    r = requests.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min",
            "forecast_days": 3,
            "timezone": "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()


def main():
    ville_saisie = sys.argv[1] if len(sys.argv) > 1 else input("Ville : ")
    try:
        ville = trouver_ville(ville_saisie)
        data = obtenir_meteo(ville["latitude"], ville["longitude"])
    except requests.exceptions.RequestException as e:
        print(f"Erreur réseau/API : {e}")
        return
    except ValueError as e:
        print(e)
        return

    actuel = data["current"]
    print(f"\nMétéo à {ville['name']} ({ville.get('country', '')})")
    print(f"Maintenant : {actuel['temperature_2m']} °C, vent {actuel['wind_speed_10m']} km/h\n")

    jours = data["daily"]
    for date, tmin, tmax in zip(
        jours["time"], jours["temperature_2m_min"], jours["temperature_2m_max"]
    ):
        print(f"{date} : min {tmin} °C / max {tmax} °C")


if __name__ == "__main__":
    main()
