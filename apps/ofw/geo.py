"""Deployment geography helpers.

Maps each OFW destination country to a representative coordinate so the OFW
deployment map can plot where monitored workers are deployed.
"""

DESTINATION_COORDINATES = {
    'Saudi Arabia': (24.7136, 46.6753),
    'UAE': (24.4539, 54.3773),
    'Qatar': (25.2854, 51.5310),
    'Kuwait': (29.3759, 47.9774),
    'Bahrain': (26.2285, 50.5860),
    'Oman': (23.5880, 58.3829),
    'Jordan': (31.9454, 35.9284),
    'Hong Kong': (22.3193, 114.1694),
    'Taiwan': (25.0330, 121.5654),
    'Singapore': (1.3521, 103.8198),
    'Malaysia': (3.1390, 101.6869),
    'Japan': (35.6762, 139.6503),
    'South Korea': (37.5665, 126.9780),
    'Macau': (22.1987, 113.5439),
    'Italy': (41.9028, 12.4964),
    'Spain': (40.4168, -3.7038),
    'United Kingdom': (51.5074, -0.1278),
    'Germany': (52.5200, 13.4050),
    'Canada': (45.4215, -75.6972),
    'United States': (38.9072, -77.0369),
}

# Representative destination city for each country (matches DESTINATION_COORDINATES).
DESTINATION_CITIES = {
    'Saudi Arabia': 'Riyadh',
    'UAE': 'Abu Dhabi',
    'Qatar': 'Doha',
    'Kuwait': 'Kuwait City',
    'Bahrain': 'Manama',
    'Oman': 'Muscat',
    'Jordan': 'Amman',
    'Hong Kong': 'Hong Kong',
    'Taiwan': 'Taipei',
    'Singapore': 'Singapore',
    'Malaysia': 'Kuala Lumpur',
    'Japan': 'Tokyo',
    'South Korea': 'Seoul',
    'Macau': 'Macau',
    'Italy': 'Rome',
    'Spain': 'Madrid',
    'United Kingdom': 'London',
    'Germany': 'Berlin',
    'Canada': 'Ottawa',
    'United States': 'Washington, D.C.',
}

# ISO 3166-1 alpha-2 codes used by the world map to highlight deployed countries.
COUNTRY_ISO = {
    'Saudi Arabia': 'SA',
    'UAE': 'AE',
    'Qatar': 'QA',
    'Kuwait': 'KW',
    'Bahrain': 'BH',
    'Oman': 'OM',
    'Jordan': 'JO',
    'Hong Kong': 'HK',
    'Taiwan': 'TW',
    'Singapore': 'SG',
    'Malaysia': 'MY',
    'Japan': 'JP',
    'South Korea': 'KR',
    'Macau': 'MO',
    'Italy': 'IT',
    'Spain': 'ES',
    'United Kingdom': 'GB',
    'Germany': 'DE',
    'Canada': 'CA',
    'United States': 'US',
}


def coordinates_for(country):
    """Return (lat, lng) for a destination country, or None if unknown."""
    return DESTINATION_COORDINATES.get(country)


def city_for(country):
    """Return a representative destination city name, or '' if unknown."""
    return DESTINATION_CITIES.get(country, '')


def iso_for(country):
    """Return the ISO 3166-1 alpha-2 code for a destination country, or None."""
    return COUNTRY_ISO.get(country)
