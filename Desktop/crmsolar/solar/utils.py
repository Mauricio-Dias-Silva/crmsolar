# utils.py ou onde estiver
import requests

def get_solar_irradiation(lat, lon, inclinacao=30, azimute=180):
    try:
        url = "https://re.jrc.ec.europa.eu/api/v5_2/seriescalc"
        params = {
            'lat': lat,
            'lon': lon,
            'angle': inclinacao,
            'aspect': azimute - 180,  # PVGIS usa -180 a +180
            'outputformat': 'json',
            'browser': 1,
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        # Extrai média diária anual (exemplo simplificado)
        monthly = data['outputs']['monthly']['fixed']
        annual_avg = sum(m['E_d'] for m in monthly) / 12
        return round(annual_avg, 2)
    except Exception as e:
        logger.exception("Erro na API PVGIS")
        return None