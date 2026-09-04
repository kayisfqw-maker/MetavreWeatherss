
import asyncio
from datetime import datetime
from typing import Optional

import flet as ft
import requests

try:
    import flet_map as ftm
except Exception:
    ftm = None

try:
    import flet_geolocator as ftg
except Exception:
    ftg = None

# Windows native Location Services fallback. This is more useful on a
# Windows desktop than IP geolocation because Windows can use Wi-Fi/GNSS
# and exposes an accuracy value.
try:
    import winrt.windows.devices.geolocation as wdg
except Exception:
    wdg = None


# ============================================================
# Metevra Weather - Flet 0.86.5
# ============================================================

FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
IP_LOCATION_URL = "https://ipapi.co/json/"
REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
TURKIYE_PROVINCES_URL = "https://api.turkiyeapi.dev/v2/provinces"
TURKIYE_DISTRICTS_URL = "https://api.turkiyeapi.dev/v2/districts"

# Armenia intentionally excluded.
EXCLUDED_COUNTRY_CODES = {"AM"}
EXCLUDED_COUNTRY_NAMES = {"Armenia", "Հայաստան", "Армения", "Arménie"}

COUNTRY_DATA = [{'code': 'AF', 'name': 'Afghanistan', 'flag': '🇦🇫'}, {'code': 'AL', 'name': 'Albania', 'flag': '🇦🇱'}, {'code': 'DZ', 'name': 'Algeria', 'flag': '🇩🇿'}, {'code': 'AS', 'name': 'American Samoa', 'flag': '🇦🇸'}, {'code': 'AD', 'name': 'Andorra', 'flag': '🇦🇩'}, {'code': 'AO', 'name': 'Angola', 'flag': '🇦🇴'}, {'code': 'AI', 'name': 'Anguilla', 'flag': '🇦🇮'}, {'code': 'AQ', 'name': 'Antarctica', 'flag': '🇦🇶'}, {'code': 'AG', 'name': 'Antigua and Barbuda', 'flag': '🇦🇬'}, {'code': 'AR', 'name': 'Argentina', 'flag': '🇦🇷'}, {'code': 'AW', 'name': 'Aruba', 'flag': '🇦🇼'}, {'code': 'AU', 'name': 'Australia', 'flag': '🇦🇺'}, {'code': 'AT', 'name': 'Austria', 'flag': '🇦🇹'}, {'code': 'AZ', 'name': 'Azerbaijan', 'flag': '🇦🇿'}, {'code': 'BS', 'name': 'Bahamas', 'flag': '🇧🇸'}, {'code': 'BH', 'name': 'Bahrain', 'flag': '🇧🇭'}, {'code': 'BD', 'name': 'Bangladesh', 'flag': '🇧🇩'}, {'code': 'BB', 'name': 'Barbados', 'flag': '🇧🇧'}, {'code': 'BY', 'name': 'Belarus', 'flag': '🇧🇾'}, {'code': 'BE', 'name': 'Belgium', 'flag': '🇧🇪'}, {'code': 'BZ', 'name': 'Belize', 'flag': '🇧🇿'}, {'code': 'BJ', 'name': 'Benin', 'flag': '🇧🇯'}, {'code': 'BM', 'name': 'Bermuda', 'flag': '🇧🇲'}, {'code': 'BT', 'name': 'Bhutan', 'flag': '🇧🇹'}, {'code': 'BO', 'name': 'Bolivia, Plurinational State of', 'flag': '🇧🇴'}, {'code': 'BQ', 'name': 'Bonaire, Sint Eustatius and Saba', 'flag': '🇧🇶'}, {'code': 'BA', 'name': 'Bosnia and Herzegovina', 'flag': '🇧🇦'}, {'code': 'BW', 'name': 'Botswana', 'flag': '🇧🇼'}, {'code': 'BV', 'name': 'Bouvet Island', 'flag': '🇧🇻'}, {'code': 'BR', 'name': 'Brazil', 'flag': '🇧🇷'}, {'code': 'IO', 'name': 'British Indian Ocean Territory', 'flag': '🇮🇴'}, {'code': 'BN', 'name': 'Brunei Darussalam', 'flag': '🇧🇳'}, {'code': 'BG', 'name': 'Bulgaria', 'flag': '🇧🇬'}, {'code': 'BF', 'name': 'Burkina Faso', 'flag': '🇧🇫'}, {'code': 'BI', 'name': 'Burundi', 'flag': '🇧🇮'}, {'code': 'CV', 'name': 'Cabo Verde', 'flag': '🇨🇻'}, {'code': 'KH', 'name': 'Cambodia', 'flag': '🇰🇭'}, {'code': 'CM', 'name': 'Cameroon', 'flag': '🇨🇲'}, {'code': 'CA', 'name': 'Canada', 'flag': '🇨🇦'}, {'code': 'KY', 'name': 'Cayman Islands', 'flag': '🇰🇾'}, {'code': 'CF', 'name': 'Central African Republic', 'flag': '🇨🇫'}, {'code': 'TD', 'name': 'Chad', 'flag': '🇹🇩'}, {'code': 'CL', 'name': 'Chile', 'flag': '🇨🇱'}, {'code': 'CN', 'name': 'China', 'flag': '🇨🇳'}, {'code': 'CX', 'name': 'Christmas Island', 'flag': '🇨🇽'}, {'code': 'CC', 'name': 'Cocos (Keeling) Islands', 'flag': '🇨🇨'}, {'code': 'CO', 'name': 'Colombia', 'flag': '🇨🇴'}, {'code': 'KM', 'name': 'Comoros', 'flag': '🇰🇲'}, {'code': 'CG', 'name': 'Congo', 'flag': '🇨🇬'}, {'code': 'CD', 'name': 'Congo, The Democratic Republic of the', 'flag': '🇨🇩'}, {'code': 'CK', 'name': 'Cook Islands', 'flag': '🇨🇰'}, {'code': 'CR', 'name': 'Costa Rica', 'flag': '🇨🇷'}, {'code': 'HR', 'name': 'Croatia', 'flag': '🇭🇷'}, {'code': 'CU', 'name': 'Cuba', 'flag': '🇨🇺'}, {'code': 'CW', 'name': 'Curaçao', 'flag': '🇨🇼'}, {'code': 'CY', 'name': 'Cyprus', 'flag': '🇨🇾'}, {'code': 'CZ', 'name': 'Czechia', 'flag': '🇨🇿'}, {'code': 'CI', 'name': "Côte d'Ivoire", 'flag': '🇨🇮'}, {'code': 'DK', 'name': 'Denmark', 'flag': '🇩🇰'}, {'code': 'DJ', 'name': 'Djibouti', 'flag': '🇩🇯'}, {'code': 'DM', 'name': 'Dominica', 'flag': '🇩🇲'}, {'code': 'DO', 'name': 'Dominican Republic', 'flag': '🇩🇴'}, {'code': 'EC', 'name': 'Ecuador', 'flag': '🇪🇨'}, {'code': 'EG', 'name': 'Egypt', 'flag': '🇪🇬'}, {'code': 'SV', 'name': 'El Salvador', 'flag': '🇸🇻'}, {'code': 'GQ', 'name': 'Equatorial Guinea', 'flag': '🇬🇶'}, {'code': 'ER', 'name': 'Eritrea', 'flag': '🇪🇷'}, {'code': 'EE', 'name': 'Estonia', 'flag': '🇪🇪'}, {'code': 'SZ', 'name': 'Eswatini', 'flag': '🇸🇿'}, {'code': 'ET', 'name': 'Ethiopia', 'flag': '🇪🇹'}, {'code': 'FK', 'name': 'Falkland Islands (Malvinas)', 'flag': '🇫🇰'}, {'code': 'FO', 'name': 'Faroe Islands', 'flag': '🇫🇴'}, {'code': 'FJ', 'name': 'Fiji', 'flag': '🇫🇯'}, {'code': 'FI', 'name': 'Finland', 'flag': '🇫🇮'}, {'code': 'FR', 'name': 'France', 'flag': '🇫🇷'}, {'code': 'GF', 'name': 'French Guiana', 'flag': '🇬🇫'}, {'code': 'PF', 'name': 'French Polynesia', 'flag': '🇵🇫'}, {'code': 'TF', 'name': 'French Southern Territories', 'flag': '🇹🇫'}, {'code': 'GA', 'name': 'Gabon', 'flag': '🇬🇦'}, {'code': 'GM', 'name': 'Gambia', 'flag': '🇬🇲'}, {'code': 'GE', 'name': 'Georgia', 'flag': '🇬🇪'}, {'code': 'DE', 'name': 'Germany', 'flag': '🇩🇪'}, {'code': 'GH', 'name': 'Ghana', 'flag': '🇬🇭'}, {'code': 'GI', 'name': 'Gibraltar', 'flag': '🇬🇮'}, {'code': 'GR', 'name': 'Greece', 'flag': '🇬🇷'}, {'code': 'GL', 'name': 'Greenland', 'flag': '🇬🇱'}, {'code': 'GD', 'name': 'Grenada', 'flag': '🇬🇩'}, {'code': 'GP', 'name': 'Guadeloupe', 'flag': '🇬🇵'}, {'code': 'GU', 'name': 'Guam', 'flag': '🇬🇺'}, {'code': 'GT', 'name': 'Guatemala', 'flag': '🇬🇹'}, {'code': 'GG', 'name': 'Guernsey', 'flag': '🇬🇬'}, {'code': 'GN', 'name': 'Guinea', 'flag': '🇬🇳'}, {'code': 'GW', 'name': 'Guinea-Bissau', 'flag': '🇬🇼'}, {'code': 'GY', 'name': 'Guyana', 'flag': '🇬🇾'}, {'code': 'HT', 'name': 'Haiti', 'flag': '🇭🇹'}, {'code': 'HM', 'name': 'Heard Island and McDonald Islands', 'flag': '🇭🇲'}, {'code': 'VA', 'name': 'Holy See (Vatican City State)', 'flag': '🇻🇦'}, {'code': 'HN', 'name': 'Honduras', 'flag': '🇭🇳'}, {'code': 'HK', 'name': 'Hong Kong', 'flag': '🇭🇰'}, {'code': 'HU', 'name': 'Hungary', 'flag': '🇭🇺'}, {'code': 'IS', 'name': 'Iceland', 'flag': '🇮🇸'}, {'code': 'IN', 'name': 'India', 'flag': '🇮🇳'}, {'code': 'ID', 'name': 'Indonesia', 'flag': '🇮🇩'}, {'code': 'IR', 'name': 'Iran, Islamic Republic of', 'flag': '🇮🇷'}, {'code': 'IQ', 'name': 'Iraq', 'flag': '🇮🇶'}, {'code': 'IE', 'name': 'Ireland', 'flag': '🇮🇪'}, {'code': 'IM', 'name': 'Isle of Man', 'flag': '🇮🇲'}, {'code': 'IL', 'name': 'Israel', 'flag': '🇮🇱'}, {'code': 'IT', 'name': 'Italy', 'flag': '🇮🇹'}, {'code': 'JM', 'name': 'Jamaica', 'flag': '🇯🇲'}, {'code': 'JP', 'name': 'Japan', 'flag': '🇯🇵'}, {'code': 'JE', 'name': 'Jersey', 'flag': '🇯🇪'}, {'code': 'JO', 'name': 'Jordan', 'flag': '🇯🇴'}, {'code': 'KZ', 'name': 'Kazakhstan', 'flag': '🇰🇿'}, {'code': 'KE', 'name': 'Kenya', 'flag': '🇰🇪'}, {'code': 'KI', 'name': 'Kiribati', 'flag': '🇰🇮'}, {'code': 'KP', 'name': "Korea, Democratic People's Republic of", 'flag': '🇰🇵'}, {'code': 'KR', 'name': 'Korea, Republic of', 'flag': '🇰🇷'}, {'code': 'KW', 'name': 'Kuwait', 'flag': '🇰🇼'}, {'code': 'KG', 'name': 'Kyrgyzstan', 'flag': '🇰🇬'}, {'code': 'LA', 'name': "Lao People's Democratic Republic", 'flag': '🇱🇦'}, {'code': 'LV', 'name': 'Latvia', 'flag': '🇱🇻'}, {'code': 'LB', 'name': 'Lebanon', 'flag': '🇱🇧'}, {'code': 'LS', 'name': 'Lesotho', 'flag': '🇱🇸'}, {'code': 'LR', 'name': 'Liberia', 'flag': '🇱🇷'}, {'code': 'LY', 'name': 'Libya', 'flag': '🇱🇾'}, {'code': 'LI', 'name': 'Liechtenstein', 'flag': '🇱🇮'}, {'code': 'LT', 'name': 'Lithuania', 'flag': '🇱🇹'}, {'code': 'LU', 'name': 'Luxembourg', 'flag': '🇱🇺'}, {'code': 'MO', 'name': 'Macao', 'flag': '🇲🇴'}, {'code': 'MG', 'name': 'Madagascar', 'flag': '🇲🇬'}, {'code': 'MW', 'name': 'Malawi', 'flag': '🇲🇼'}, {'code': 'MY', 'name': 'Malaysia', 'flag': '🇲🇾'}, {'code': 'MV', 'name': 'Maldives', 'flag': '🇲🇻'}, {'code': 'ML', 'name': 'Mali', 'flag': '🇲🇱'}, {'code': 'MT', 'name': 'Malta', 'flag': '🇲🇹'}, {'code': 'MH', 'name': 'Marshall Islands', 'flag': '🇲🇭'}, {'code': 'MQ', 'name': 'Martinique', 'flag': '🇲🇶'}, {'code': 'MR', 'name': 'Mauritania', 'flag': '🇲🇷'}, {'code': 'MU', 'name': 'Mauritius', 'flag': '🇲🇺'}, {'code': 'YT', 'name': 'Mayotte', 'flag': '🇾🇹'}, {'code': 'MX', 'name': 'Mexico', 'flag': '🇲🇽'}, {'code': 'FM', 'name': 'Micronesia, Federated States of', 'flag': '🇫🇲'}, {'code': 'MD', 'name': 'Moldova, Republic of', 'flag': '🇲🇩'}, {'code': 'MC', 'name': 'Monaco', 'flag': '🇲🇨'}, {'code': 'MN', 'name': 'Mongolia', 'flag': '🇲🇳'}, {'code': 'ME', 'name': 'Montenegro', 'flag': '🇲🇪'}, {'code': 'MS', 'name': 'Montserrat', 'flag': '🇲🇸'}, {'code': 'MA', 'name': 'Morocco', 'flag': '🇲🇦'}, {'code': 'MZ', 'name': 'Mozambique', 'flag': '🇲🇿'}, {'code': 'MM', 'name': 'Myanmar', 'flag': '🇲🇲'}, {'code': 'NA', 'name': 'Namibia', 'flag': '🇳🇦'}, {'code': 'NR', 'name': 'Nauru', 'flag': '🇳🇷'}, {'code': 'NP', 'name': 'Nepal', 'flag': '🇳🇵'}, {'code': 'NL', 'name': 'Netherlands', 'flag': '🇳🇱'}, {'code': 'NC', 'name': 'New Caledonia', 'flag': '🇳🇨'}, {'code': 'NZ', 'name': 'New Zealand', 'flag': '🇳🇿'}, {'code': 'NI', 'name': 'Nicaragua', 'flag': '🇳🇮'}, {'code': 'NE', 'name': 'Niger', 'flag': '🇳🇪'}, {'code': 'NG', 'name': 'Nigeria', 'flag': '🇳🇬'}, {'code': 'NU', 'name': 'Niue', 'flag': '🇳🇺'}, {'code': 'NF', 'name': 'Norfolk Island', 'flag': '🇳🇫'}, {'code': 'MK', 'name': 'North Macedonia', 'flag': '🇲🇰'}, {'code': 'MP', 'name': 'Northern Mariana Islands', 'flag': '🇲🇵'}, {'code': 'NO', 'name': 'Norway', 'flag': '🇳🇴'}, {'code': 'OM', 'name': 'Oman', 'flag': '🇴🇲'}, {'code': 'PK', 'name': 'Pakistan', 'flag': '🇵🇰'}, {'code': 'PW', 'name': 'Palau', 'flag': '🇵🇼'}, {'code': 'PS', 'name': 'Palestine, State of', 'flag': '🇵🇸'}, {'code': 'PA', 'name': 'Panama', 'flag': '🇵🇦'}, {'code': 'PG', 'name': 'Papua New Guinea', 'flag': '🇵🇬'}, {'code': 'PY', 'name': 'Paraguay', 'flag': '🇵🇾'}, {'code': 'PE', 'name': 'Peru', 'flag': '🇵🇪'}, {'code': 'PH', 'name': 'Philippines', 'flag': '🇵🇭'}, {'code': 'PN', 'name': 'Pitcairn', 'flag': '🇵🇳'}, {'code': 'PL', 'name': 'Poland', 'flag': '🇵🇱'}, {'code': 'PT', 'name': 'Portugal', 'flag': '🇵🇹'}, {'code': 'PR', 'name': 'Puerto Rico', 'flag': '🇵🇷'}, {'code': 'QA', 'name': 'Qatar', 'flag': '🇶🇦'}, {'code': 'RO', 'name': 'Romania', 'flag': '🇷🇴'}, {'code': 'RU', 'name': 'Russian Federation', 'flag': '🇷🇺'}, {'code': 'RW', 'name': 'Rwanda', 'flag': '🇷🇼'}, {'code': 'RE', 'name': 'Réunion', 'flag': '🇷🇪'}, {'code': 'BL', 'name': 'Saint Barthélemy', 'flag': '🇧🇱'}, {'code': 'SH', 'name': 'Saint Helena, Ascension and Tristan da Cunha', 'flag': '🇸🇭'}, {'code': 'KN', 'name': 'Saint Kitts and Nevis', 'flag': '🇰🇳'}, {'code': 'LC', 'name': 'Saint Lucia', 'flag': '🇱🇨'}, {'code': 'MF', 'name': 'Saint Martin (French part)', 'flag': '🇲🇫'}, {'code': 'PM', 'name': 'Saint Pierre and Miquelon', 'flag': '🇵🇲'}, {'code': 'VC', 'name': 'Saint Vincent and the Grenadines', 'flag': '🇻🇨'}, {'code': 'WS', 'name': 'Samoa', 'flag': '🇼🇸'}, {'code': 'SM', 'name': 'San Marino', 'flag': '🇸🇲'}, {'code': 'ST', 'name': 'Sao Tome and Principe', 'flag': '🇸🇹'}, {'code': 'SA', 'name': 'Saudi Arabia', 'flag': '🇸🇦'}, {'code': 'SN', 'name': 'Senegal', 'flag': '🇸🇳'}, {'code': 'RS', 'name': 'Serbia', 'flag': '🇷🇸'}, {'code': 'SC', 'name': 'Seychelles', 'flag': '🇸🇨'}, {'code': 'SL', 'name': 'Sierra Leone', 'flag': '🇸🇱'}, {'code': 'SG', 'name': 'Singapore', 'flag': '🇸🇬'}, {'code': 'SX', 'name': 'Sint Maarten (Dutch part)', 'flag': '🇸🇽'}, {'code': 'SK', 'name': 'Slovakia', 'flag': '🇸🇰'}, {'code': 'SI', 'name': 'Slovenia', 'flag': '🇸🇮'}, {'code': 'SB', 'name': 'Solomon Islands', 'flag': '🇸🇧'}, {'code': 'SO', 'name': 'Somalia', 'flag': '🇸🇴'}, {'code': 'ZA', 'name': 'South Africa', 'flag': '🇿🇦'}, {'code': 'GS', 'name': 'South Georgia and the South Sandwich Islands', 'flag': '🇬🇸'}, {'code': 'SS', 'name': 'South Sudan', 'flag': '🇸🇸'}, {'code': 'ES', 'name': 'Spain', 'flag': '🇪🇸'}, {'code': 'LK', 'name': 'Sri Lanka', 'flag': '🇱🇰'}, {'code': 'SD', 'name': 'Sudan', 'flag': '🇸🇩'}, {'code': 'SR', 'name': 'Suriname', 'flag': '🇸🇷'}, {'code': 'SJ', 'name': 'Svalbard and Jan Mayen', 'flag': '🇸🇯'}, {'code': 'SE', 'name': 'Sweden', 'flag': '🇸🇪'}, {'code': 'CH', 'name': 'Switzerland', 'flag': '🇨🇭'}, {'code': 'SY', 'name': 'Syrian Arab Republic', 'flag': '🇸🇾'}, {'code': 'TW', 'name': 'Taiwan, Province of China', 'flag': '🇹🇼'}, {'code': 'TJ', 'name': 'Tajikistan', 'flag': '🇹🇯'}, {'code': 'TZ', 'name': 'Tanzania, United Republic of', 'flag': '🇹🇿'}, {'code': 'TH', 'name': 'Thailand', 'flag': '🇹🇭'}, {'code': 'TL', 'name': 'Timor-Leste', 'flag': '🇹🇱'}, {'code': 'TG', 'name': 'Togo', 'flag': '🇹🇬'}, {'code': 'TK', 'name': 'Tokelau', 'flag': '🇹🇰'}, {'code': 'TO', 'name': 'Tonga', 'flag': '🇹🇴'}, {'code': 'TT', 'name': 'Trinidad and Tobago', 'flag': '🇹🇹'}, {'code': 'TN', 'name': 'Tunisia', 'flag': '🇹🇳'}, {'code': 'TM', 'name': 'Turkmenistan', 'flag': '🇹🇲'}, {'code': 'TC', 'name': 'Turks and Caicos Islands', 'flag': '🇹🇨'}, {'code': 'TV', 'name': 'Tuvalu', 'flag': '🇹🇻'}, {'code': 'TR', 'name': 'Türkiye', 'flag': '🇹🇷'}, {'code': 'UG', 'name': 'Uganda', 'flag': '🇺🇬'}, {'code': 'UA', 'name': 'Ukraine', 'flag': '🇺🇦'}, {'code': 'AE', 'name': 'United Arab Emirates', 'flag': '🇦🇪'}, {'code': 'GB', 'name': 'United Kingdom', 'flag': '🇬🇧'}, {'code': 'US', 'name': 'United States', 'flag': '🇺🇸'}, {'code': 'UM', 'name': 'United States Minor Outlying Islands', 'flag': '🇺🇲'}, {'code': 'UY', 'name': 'Uruguay', 'flag': '🇺🇾'}, {'code': 'UZ', 'name': 'Uzbekistan', 'flag': '🇺🇿'}, {'code': 'VU', 'name': 'Vanuatu', 'flag': '🇻🇺'}, {'code': 'VE', 'name': 'Venezuela, Bolivarian Republic of', 'flag': '🇻🇪'}, {'code': 'VN', 'name': 'Viet Nam', 'flag': '🇻🇳'}, {'code': 'VG', 'name': 'Virgin Islands, British', 'flag': '🇻🇬'}, {'code': 'VI', 'name': 'Virgin Islands, U.S.', 'flag': '🇻🇮'}, {'code': 'WF', 'name': 'Wallis and Futuna', 'flag': '🇼🇫'}, {'code': 'EH', 'name': 'Western Sahara', 'flag': '🇪🇭'}, {'code': 'YE', 'name': 'Yemen', 'flag': '🇾🇪'}, {'code': 'ZM', 'name': 'Zambia', 'flag': '🇿🇲'}, {'code': 'ZW', 'name': 'Zimbabwe', 'flag': '🇿🇼'}, {'code': 'AX', 'name': 'Åland Islands', 'flag': '🇦🇽'}]

LANG = {
    "EN": {"title":"Metevra Weather","search_country":"Search country...","search_city":"Search city...","find_location":"Find my location","loading":"Loading...","current":"Current Weather","hourly":"12-Hour Forecast","daily":"15-Day Forecast","humidity":"Humidity","wind":"Wind","pressure":"Pressure","precip":"Precipitation","feels":"Feels like","sunrise":"Sunrise","sunset":"Sunset","sun":"Sun","lightning":"Lightning risk","radar":"Radar","map":"Map","road":"Road","earth":"Earth","terrain":"Terrain","country":"Country","province":"Province","district":"District","search_error":"Location not found.","network_error":"Check your internet connection.","location_error":"Could not get your location.","today":"Today","now":"Now","day":"Day","night":"Night","low":"Low","medium":"Medium","high":"High","select_country":"Select a country first","select_province":"Select a province","select_district":"Select a district","weather":"Weather","cloud":"Cloud cover","source":"Weather data: Open-Meteo","radar_source":"Radar: RainViewer"},
    "TR": {"title":"Metevra Weather","search_country":"Ülke ara...","search_city":"Şehir ara...","find_location":"Konumumu bul","loading":"Yükleniyor...","current":"Güncel Hava","hourly":"12 Saatlik Tahmin","daily":"15 Günlük Tahmin","humidity":"Nem","wind":"Rüzgar","pressure":"Basınç","precip":"Yağış","feels":"Hissedilen","sunrise":"Gün doğumu","sunset":"Gün batımı","sun":"Güneş","lightning":"Yıldırım riski","radar":"Radar","map":"Harita","road":"Yol","earth":"Uydu","terrain":"Arazi","country":"Ülke","province":"İl","district":"İlçe","search_error":"Konum bulunamadı.","network_error":"İnternet bağlantısını kontrol edin.","location_error":"Konum alınamadı.","today":"Bugün","now":"Şimdi","day":"Gündüz","night":"Gece","low":"Düşük","medium":"Orta","high":"Yüksek","select_country":"Önce ülke seçin","select_province":"İl seçin","select_district":"İlçe seçin","weather":"Hava Durumu","cloud":"Bulutluluk","source":"Hava verisi: Open-Meteo","radar_source":"Radar: RainViewer"},
    "DE": {"title":"Metevra Weather","search_country":"Land suchen...","search_city":"Stadt suchen...","find_location":"Meinen Standort finden","loading":"Laden...","current":"Aktuelles Wetter","hourly":"12-Stunden-Prognose","daily":"15-Tage-Prognose","humidity":"Feuchtigkeit","wind":"Wind","pressure":"Druck","precip":"Niederschlag","feels":"Gefühlt","sunrise":"Sonnenaufgang","sunset":"Sonnenuntergang","sun":"Sonne","lightning":"Blitzrisiko","radar":"Radar","map":"Karte","road":"Straße","earth":"Satellit","terrain":"Gelände","country":"Land","province":"Provinz","district":"Bezirk","search_error":"Ort nicht gefunden.","network_error":"Internetverbindung prüfen.","location_error":"Standort konnte nicht ermittelt werden.","today":"Heute","now":"Jetzt","day":"Tag","night":"Nacht","low":"Niedrig","medium":"Mittel","high":"Hoch","select_country":"Zuerst Land auswählen","select_province":"Provinz auswählen","select_district":"Bezirk auswählen","weather":"Wetter","cloud":"Bewölkung","source":"Wetterdaten: Open-Meteo","radar_source":"Radar: RainViewer"},
    "FR": {"title":"Metevra Weather","search_country":"Rechercher un pays...","search_city":"Rechercher une ville...","find_location":"Trouver ma position","loading":"Chargement...","current":"Météo actuelle","hourly":"Prévisions 12 heures","daily":"Prévisions 15 jours","humidity":"Humidité","wind":"Vent","pressure":"Pression","precip":"Précipitations","feels":"Ressenti","sunrise":"Lever du soleil","sunset":"Coucher du soleil","sun":"Soleil","lightning":"Risque de foudre","radar":"Radar","map":"Carte","road":"Route","earth":"Satellite","terrain":"Terrain","country":"Pays","province":"Région","district":"District","search_error":"Lieu introuvable.","network_error":"Vérifiez votre connexion Internet.","location_error":"Position introuvable.","today":"Aujourd'hui","now":"Maintenant","day":"Jour","night":"Nuit","low":"Faible","medium":"Moyen","high":"Élevé","select_country":"Sélectionnez d'abord un pays","select_province":"Sélectionner une région","select_district":"Sélectionner un district","weather":"Météo","cloud":"Nuages","source":"Données météo : Open-Meteo","radar_source":"Radar : RainViewer"},
    "ES": {"title":"Metevra Weather","search_country":"Buscar país...","search_city":"Buscar ciudad...","find_location":"Encontrar mi ubicación","loading":"Cargando...","current":"Tiempo actual","hourly":"Pronóstico de 12 horas","daily":"Pronóstico de 15 días","humidity":"Humedad","wind":"Viento","pressure":"Presión","precip":"Precipitación","feels":"Sensación","sunrise":"Amanecer","sunset":"Atardecer","sun":"Sol","lightning":"Riesgo de rayos","radar":"Radar","map":"Mapa","road":"Carretera","earth":"Satélite","terrain":"Terreno","country":"País","province":"Provincia","district":"Distrito","search_error":"Ubicación no encontrada.","network_error":"Comprueba tu conexión a Internet.","location_error":"No se pudo obtener la ubicación.","today":"Hoy","now":"Ahora","day":"Día","night":"Noche","low":"Bajo","medium":"Medio","high":"Alto","select_country":"Selecciona primero un país","select_province":"Selecciona una provincia","select_district":"Selecciona un distrito","weather":"Tiempo","cloud":"Nubosidad","source":"Datos meteorológicos: Open-Meteo","radar_source":"Radar: RainViewer"},
    "IT": {"title":"Metevra Weather","search_country":"Cerca paese...","search_city":"Cerca città...","find_location":"Trova la mia posizione","loading":"Caricamento...","current":"Meteo attuale","hourly":"Previsioni 12 ore","daily":"Previsioni 15 giorni","humidity":"Umidità","wind":"Vento","pressure":"Pressione","precip":"Precipitazioni","feels":"Percepita","sunrise":"Alba","sunset":"Tramonto","sun":"Sole","lightning":"Rischio fulmini","radar":"Radar","map":"Mappa","road":"Strada","earth":"Satellite","terrain":"Terreno","country":"Paese","province":"Provincia","district":"Distretto","search_error":"Posizione non trovata.","network_error":"Controlla la connessione Internet.","location_error":"Impossibile ottenere la posizione.","today":"Oggi","now":"Ora","day":"Giorno","night":"Notte","low":"Basso","medium":"Medio","high":"Alto","select_country":"Seleziona prima un paese","select_province":"Seleziona una provincia","select_district":"Seleziona un distretto","weather":"Meteo","cloud":"Nuvole","source":"Dati meteo: Open-Meteo","radar_source":"Radar: RainViewer"},
    "PT": {"title":"Metevra Weather","search_country":"Pesquisar país...","search_city":"Pesquisar cidade...","find_location":"Encontrar minha localização","loading":"A carregar...","current":"Tempo atual","hourly":"Previsão de 12 horas","daily":"Previsão de 15 dias","humidity":"Humidade","wind":"Vento","pressure":"Pressão","precip":"Precipitação","feels":"Sensação","sunrise":"Nascer do sol","sunset":"Pôr do sol","sun":"Sol","lightning":"Risco de relâmpagos","radar":"Radar","map":"Mapa","road":"Estrada","earth":"Satélite","terrain":"Terreno","country":"País","province":"Província","district":"Distrito","search_error":"Localização não encontrada.","network_error":"Verifique a ligação à Internet.","location_error":"Não foi possível obter a localização.","today":"Hoje","now":"Agora","day":"Dia","night":"Noite","low":"Baixo","medium":"Médio","high":"Alto","select_country":"Selecione primeiro um país","select_province":"Selecione uma província","select_district":"Selecione um distrito","weather":"Tempo","cloud":"Nuvens","source":"Dados meteorológicos: Open-Meteo","radar_source":"Radar: RainViewer"},
}

# Global UI languages. Country detection selects the closest supported language.
_EXTRA_LANG = {
    "RU": {"search_country":"Поиск страны...","search_city":"Поиск города...","find_location":"Моё местоположение","loading":"Загрузка...","current":"Текущая погода","hourly":"12-часовой прогноз","daily":"Прогноз на 7 дней","humidity":"Влажность","wind":"Ветер","pressure":"Давление","precip":"Осадки","feels":"Ощущается как","sunrise":"Восход","sunset":"Закат","day":"День","night":"Ночь","low":"Низкий","medium":"Средний","high":"Высокий","select_country":"Сначала выберите страну","select_province":"Выберите регион","select_district":"Выберите район","map":"Карта","road":"Дорога","earth":"Спутник","terrain":"Рельеф","radar":"Радар","country":"Страна","province":"Регион","district":"Район","search_error":"Место не найдено.","network_error":"Проверьте интернет-соединение.","location_error":"Не удалось определить местоположение.","today":"Сегодня","now":"Сейчас","cloud":"Облачность","source":"Источник: Open-Meteo","radar_source":"Радар: RainViewer","language":"Язык","title":"Metevra Weather"},
    "AR": {"search_country":"ابحث عن دولة...","search_city":"ابحث عن مدينة...","find_location":"العثور على موقعي","loading":"جارٍ التحميل...","current":"الطقس الحالي","hourly":"توقعات 12 ساعة","daily":"توقعات 7 أيام","humidity":"الرطوبة","wind":"الرياح","pressure":"الضغط","precip":"الهطول","feels":"المحسوسة","sunrise":"شروق الشمس","sunset":"غروب الشمس","day":"نهار","night":"ليل","low":"منخفض","medium":"متوسط","high":"مرتفع","select_country":"اختر الدولة أولاً","select_province":"اختر المنطقة","select_district":"اختر المنطقة الفرعية","map":"الخريطة","road":"الطرق","earth":"القمر الصناعي","terrain":"التضاريس","radar":"الرادار","country":"الدولة","province":"المنطقة","district":"المنطقة الفرعية","search_error":"لم يتم العثور على الموقع.","network_error":"تحقق من اتصال الإنترنت.","location_error":"تعذر الحصول على الموقع.","today":"اليوم","now":"الآن","cloud":"السحب","source":"المصدر: Open-Meteo","radar_source":"الرادار: RainViewer","language":"اللغة","title":"Metevra Weather"},
    "ZH": {"search_country":"搜索国家...","search_city":"搜索城市...","find_location":"查找我的位置","loading":"加载中...","current":"当前天气","hourly":"12小时预报","daily":"7天天气预报","humidity":"湿度","wind":"风","pressure":"气压","precip":"降水","feels":"体感温度","sunrise":"日出","sunset":"日落","day":"白天","night":"夜间","low":"低","medium":"中","high":"高","select_country":"请先选择国家","select_province":"选择省/州","select_district":"选择地区","map":"地图","road":"道路","earth":"卫星","terrain":"地形","radar":"雷达","country":"国家","province":"省/州","district":"地区","search_error":"找不到位置。","network_error":"请检查网络连接。","location_error":"无法获取位置。","today":"今天","now":"现在","cloud":"云量","source":"数据来源：Open-Meteo","radar_source":"雷达：RainViewer","language":"语言","title":"Metevra Weather"},
    "JA": {"search_country":"国を検索...","search_city":"都市を検索...","find_location":"現在地を取得","loading":"読み込み中...","current":"現在の天気","hourly":"12時間予報","daily":"7日間予報","humidity":"湿度","wind":"風","pressure":"気圧","precip":"降水量","feels":"体感温度","sunrise":"日の出","sunset":"日の入り","day":"昼","night":"夜","low":"低","medium":"中","high":"高","select_country":"先に国を選択","select_province":"地域を選択","select_district":"地区を選択","map":"地図","road":"道路","earth":"衛星","terrain":"地形","radar":"レーダー","country":"国","province":"地域","district":"地区","search_error":"場所が見つかりません。","network_error":"インターネット接続を確認してください。","location_error":"位置情報を取得できません。","today":"今日","now":"現在","cloud":"雲量","source":"データ: Open-Meteo","radar_source":"レーダー: RainViewer","language":"言語","title":"Metevra Weather"},
    "KO": {"search_country":"국가 검색...","search_city":"도시 검색...","find_location":"내 위치 찾기","loading":"로딩 중...","current":"현재 날씨","hourly":"12시간 예보","daily":"7일 예보","humidity":"습도","wind":"바람","pressure":"기압","precip":"강수량","feels":"체감 온도","sunrise":"일출","sunset":"일몰","day":"낮","night":"밤","low":"낮음","medium":"보통","high":"높음","select_country":"먼저 국가를 선택하세요","select_province":"지역 선택","select_district":"구역 선택","map":"지도","road":"도로","earth":"위성","terrain":"지형","radar":"레이더","country":"국가","province":"지역","district":"구역","search_error":"위치를 찾을 수 없습니다.","network_error":"인터넷 연결을 확인하세요.","location_error":"위치를 가져올 수 없습니다.","today":"오늘","now":"현재","cloud":"구름","source":"데이터: Open-Meteo","radar_source":"레이더: RainViewer","language":"언어","title":"Metevra Weather"},
    "HI": {"search_country":"देश खोजें...","search_city":"शहर खोजें...","find_location":"मेरा स्थान खोजें","loading":"लोड हो रहा है...","current":"वर्तमान मौसम","hourly":"12 घंटे का पूर्वानुमान","daily":"7-दिन का पूर्वानुमान","humidity":"नमी","wind":"हवा","pressure":"दबाव","precip":"वर्षा","feels":"महसूस होने वाला तापमान","sunrise":"सूर्योदय","sunset":"सूर्यास्त","day":"दिन","night":"रात","low":"कम","medium":"मध्यम","high":"उच्च","select_country":"पहले देश चुनें","select_province":"राज्य चुनें","select_district":"जिला चुनें","map":"मानचित्र","road":"सड़क","earth":"उपग्रह","terrain":"भूभाग","radar":"रडार","country":"देश","province":"राज्य","district":"जिला","search_error":"स्थान नहीं मिला।","network_error":"इंटरनेट कनेक्शन जांचें।","location_error":"स्थान प्राप्त नहीं किया जा सका।","today":"आज","now":"अभी","cloud":"बादल","source":"स्रोत: Open-Meteo","radar_source":"रडार: RainViewer","language":"भाषा","title":"Metevra Weather"},
    "ID": {"search_country":"Cari negara...","search_city":"Cari kota...","find_location":"Temukan lokasi saya","loading":"Memuat...","current":"Cuaca Saat Ini","hourly":"Prakiraan 12 Jam","daily":"Prakiraan 7 Hari","humidity":"Kelembapan","wind":"Angin","pressure":"Tekanan","precip":"Curah hujan","feels":"Terasa seperti","sunrise":"Matahari terbit","sunset":"Matahari terbenam","day":"Siang","night":"Malam","low":"Rendah","medium":"Sedang","high":"Tinggi","select_country":"Pilih negara terlebih dahulu","select_province":"Pilih provinsi","select_district":"Pilih distrik","map":"Peta","road":"Jalan","earth":"Satelit","terrain":"Medan","radar":"Radar","country":"Negara","province":"Provinsi","district":"Distrik","search_error":"Lokasi tidak ditemukan.","network_error":"Periksa koneksi internet.","location_error":"Lokasi tidak dapat ditemukan.","today":"Hari ini","now":"Sekarang","cloud":"Tutupan awan","source":"Sumber: Open-Meteo","radar_source":"Radar: RainViewer","language":"Bahasa","title":"Metevra Weather"},
    "NL": {"search_country":"Land zoeken...","search_city":"Stad zoeken...","find_location":"Mijn locatie vinden","loading":"Laden...","current":"Huidig weer","hourly":"12-uursverwachting","daily":"7-daagse verwachting","humidity":"Vochtigheid","wind":"Wind","pressure":"Luchtdruk","precip":"Neerslag","feels":"Gevoelstemperatuur","sunrise":"Zonsopkomst","sunset":"Zonsondergang","day":"Dag","night":"Nacht","low":"Laag","medium":"Gemiddeld","high":"Hoog","select_country":"Kies eerst een land","select_province":"Kies provincie","select_district":"Kies district","map":"Kaart","road":"Weg","earth":"Satelliet","terrain":"Terrein","radar":"Radar","country":"Land","province":"Provincie","district":"District","search_error":"Locatie niet gevonden.","network_error":"Controleer je internetverbinding.","location_error":"Locatie kon niet worden bepaald.","today":"Vandaag","now":"Nu","cloud":"Bewolking","source":"Bron: Open-Meteo","radar_source":"Radar: RainViewer","language":"Taal","title":"Metevra Weather"},
    "PL": {"search_country":"Szukaj kraju...","search_city":"Szukaj miasta...","find_location":"Znajdź moją lokalizację","loading":"Ładowanie...","current":"Aktualna pogoda","hourly":"Prognoza 12-godzinna","daily":"Prognoza 7-dniowa","humidity":"Wilgotność","wind":"Wiatr","pressure":"Ciśnienie","precip":"Opady","feels":"Odczuwalna","sunrise":"Wschód słońca","sunset":"Zachód słońca","day":"Dzień","night":"Noc","low":"Niski","medium":"Średni","high":"Wysoki","select_country":"Najpierw wybierz kraj","select_province":"Wybierz region","select_district":"Wybierz powiat","map":"Mapa","road":"Droga","earth":"Satelita","terrain":"Teren","radar":"Radar","country":"Kraj","province":"Region","district":"Powiat","search_error":"Nie znaleziono lokalizacji.","network_error":"Sprawdź połączenie z internetem.","location_error":"Nie można pobrać lokalizacji.","today":"Dzisiaj","now":"Teraz","cloud":"Zachmurzenie","source":"Źródło: Open-Meteo","radar_source":"Radar: RainViewer","language":"Język","title":"Metevra Weather"},
    "SV": {"search_country":"Sök land...","search_city":"Sök stad...","find_location":"Hitta min plats","loading":"Laddar...","current":"Aktuellt väder","hourly":"12-timmarsprognos","daily":"7-dagars prognos","humidity":"Luftfuktighet","wind":"Vind","pressure":"Lufttryck","precip":"Nederbörd","feels":"Känns som","sunrise":"Soluppgång","sunset":"Solnedgång","day":"Dag","night":"Natt","low":"Låg","medium":"Medel","high":"Hög","select_country":"Välj land först","select_province":"Välj region","select_district":"Välj distrikt","map":"Karta","road":"Väg","earth":"Satellit","terrain":"Terräng","radar":"Radar","country":"Land","province":"Region","district":"Distrikt","search_error":"Platsen hittades inte.","network_error":"Kontrollera internetanslutningen.","location_error":"Kunde inte hitta platsen.","today":"Idag","now":"Nu","cloud":"Molnighet","source":"Källa: Open-Meteo","radar_source":"Radar: RainViewer","language":"Språk","title":"Metevra Weather"},
    "UK": {"search_country":"Пошук країни...","search_city":"Пошук міста...","find_location":"Знайти моє місцезнаходження","loading":"Завантаження...","current":"Поточна погода","hourly":"12-годинний прогноз","daily":"Прогноз на 7 днів","humidity":"Вологість","wind":"Вітер","pressure":"Тиск","precip":"Опади","feels":"Відчувається як","sunrise":"Схід сонця","sunset":"Захід сонця","day":"День","night":"Ніч","low":"Низький","medium":"Середній","high":"Високий","select_country":"Спочатку виберіть країну","select_province":"Виберіть область","select_district":"Виберіть район","map":"Мапа","road":"Дорога","earth":"Супутник","terrain":"Рельєф","radar":"Радар","country":"Країна","province":"Область","district":"Район","search_error":"Місце не знайдено.","network_error":"Перевірте підключення до Інтернету.","location_error":"Не вдалося отримати місцезнаходження.","today":"Сьогодні","now":"Зараз","cloud":"Хмарність","source":"Джерело: Open-Meteo","radar_source":"Радар: RainViewer","language":"Мова","title":"Metevra Weather"},
}
for _k, _v in _EXTRA_LANG.items():
    LANG[_k] = {**LANG["EN"], **_v}

LANG_NAMES = {
    "TR":"Türkçe","EN":"English","DE":"Deutsch","FR":"Français","ES":"Español",
    "IT":"Italiano","PT":"Português","RU":"Русский","AR":"العربية","ZH":"中文",
    "JA":"日本語","KO":"한국어","HI":"हिन्दी","ID":"Bahasa Indonesia",
    "NL":"Nederlands","PL":"Polski","SV":"Svenska","UK":"Українська"
}

COUNTRY_LANGUAGE = {}
for _cc in """TR""".split():
    COUNTRY_LANGUAGE[_cc] = "TR"

for _cc in """DE AT CH LI LU
GB US CA AU NZ IE SG ZA IN PH
FR BE MC
ES MX AR CL CO PE VE UY PY BO EC CR PA DO CU GT HN SV NI
IT SM VA
PT BR AO MZ
RU BY KZ KG TJ TM UZ
UA
NL
PL
SE FI
AR SA AE QA KW BH OM JO LB EG MA DZ TN
CN TW
JP
KR
ID MY
HI IN
""".split():
    if _cc in COUNTRY_LANGUAGE:
        continue
    # Country groups are resolved below with the first suitable supported language.
    COUNTRY_LANGUAGE[_cc] = {
        "DE":"DE","AT":"DE","CH":"DE","LI":"DE","LU":"DE",
        "GB":"EN","US":"EN","CA":"EN","AU":"EN","NZ":"EN","IE":"EN","SG":"EN","ZA":"EN","PH":"EN",
        "FR":"FR","BE":"FR","MC":"FR",
        "ES":"ES","MX":"ES","AR":"ES","CL":"ES","CO":"ES","PE":"ES","VE":"ES","UY":"ES","PY":"ES","BO":"ES","EC":"ES","CR":"ES","PA":"ES","DO":"ES","CU":"ES","GT":"ES","HN":"ES","SV":"ES","NI":"ES",
        "IT":"IT","SM":"IT","VA":"IT",
        "PT":"PT","BR":"PT","AO":"PT","MZ":"PT",
        "RU":"RU","BY":"RU","KZ":"RU","KG":"RU","TJ":"RU","TM":"RU",
        "UA":"UK","NL":"NL","PL":"PL","SE":"SV","FI":"EN",
        "AR":"AR","SA":"AR","AE":"AR","QA":"AR","KW":"AR","BH":"AR","OM":"AR","JO":"AR","LB":"AR","EG":"AR","MA":"AR","DZ":"AR","TN":"AR",
        "CN":"ZH","TW":"ZH","JP":"JA","KR":"KO","ID":"ID","MY":"ID","IN":"HI"
    }.get(_cc, "EN")


WEATHER = {
    0:"☀️",1:"🌤️",2:"⛅",3:"☁️",45:"🌫️",48:"🌫️",
    51:"🌦️",53:"🌦️",55:"🌧️",56:"🌧️",57:"🌧️",
    61:"🌧️",63:"🌧️",65:"🌧️",66:"🌧️",67:"🌧️",
    71:"🌨️",73:"🌨️",75:"❄️",77:"❄️",80:"🌦️",81:"🌧️",
    82:"⛈️",85:"🌨️",86:"❄️",95:"⛈️",96:"⛈️",99:"⛈️",
}

def weather_icon(code):
    return WEATHER.get(int(code or 0), "🌤️")

def request_json(url, params=None, timeout=15):
    r = requests.get(url, params=params, timeout=timeout,
                     headers={"User-Agent":"MetevraWeather/1.0 (weather app)"})
    r.raise_for_status()
    return r.json()

def geocode_city(query, language="en", country_code=None):
    params = {"name": query, "count": 10, "language": language, "format":"json"}
    if country_code:
        params["countryCode"] = country_code.lower()
    return request_json(GEOCODING_URL, params, 12).get("results") or []

async def get_windows_location():
    """Get a fresh, high-accuracy position from Windows Location Services.

    We intentionally do NOT fall back to IP geolocation here. An IP address
    can resolve to the ISP's registered city and produce a misleading result
    such as Atakum/Samsun.
    """
    if wdg is None:
        raise RuntimeError("Windows Location API is not installed")

    # Microsoft recommends requesting access before reading a position.
    locator = wdg.Geolocator()

    # Ask Windows for the highest practical accuracy. Windows documents that
    # HIGH corresponds to a 10 m desired accuracy, when the hardware/source
    # can actually provide it.
    try:
        locator.desired_accuracy_in_meters = 10
    except Exception:
        try:
            locator.desired_accuracy = wdg.PositionAccuracy.HIGH
        except Exception:
            pass

    request_access = getattr(locator, "request_access_async", None)
    if request_access is not None:
        access = await request_access()
        access_text = str(access).lower()
        if "denied" in access_text or "unspecified" in access_text:
            raise PermissionError(f"Windows location access: {access}")

    # Ask Windows for a current fix rather than silently accepting an old
    # cached/default position. 20 seconds is enough for Wi-Fi based fixes.
    position = await locator.get_geoposition_async()
    coordinate = position.coordinate
    point = coordinate.point.position
    lat = float(point.latitude)
    lon = float(point.longitude)
    accuracy = getattr(coordinate, "accuracy", None)

    # If Windows reports an extremely coarse result, do not pretend it is
    # precise. The caller will show an error and the user can retry after
    # enabling Windows Location Services / Wi-Fi positioning.
    if accuracy is not None:
        try:
            accuracy = float(accuracy)
            if accuracy > 10000:
                raise RuntimeError(f"Windows returned a coarse position: {accuracy:.0f} m")
        except ValueError:
            pass

    return lat, lon, accuracy


def get_ip_location():
    d = request_json(IP_LOCATION_URL, timeout=8)
    return float(d["latitude"]), float(d["longitude"]), d.get("city") or "", d.get("country_code") or ""

def get_countries():
    return [dict(x) for x in COUNTRY_DATA if x["code"] not in EXCLUDED_COUNTRY_CODES]

def get_turkiye_provinces():
    d = request_json(TURKIYE_PROVINCES_URL, {"fields":"id,name","limit":100,"sort":"name"}, 12)
    return d.get("data") or []

def get_turkiye_districts(province_id):
    d = request_json(
        TURKIYE_DISTRICTS_URL,
        {"provinceId": int(province_id), "fields": "id,name,provinceId", "limit": 1000, "sort": "name"},
        12,
    )
    return d.get("data") or []

def reverse_country(lat, lon):
    try:
        d = request_json(REVERSE_URL, {"lat":lat,"lon":lon,"format":"json","zoom":3}, 10)
        a = d.get("address") or {}
        return (a.get("country_code") or "").upper(), a.get("country") or ""
    except Exception:
        return "", ""

def reverse_location(lat, lon):
    """Return the most useful city/district/province/country name for GPS."""
    try:
        d = request_json(
            REVERSE_URL,
            {
                "lat": lat, "lon": lon, "format": "json", "zoom": 18,
                "addressdetails": 1, "accept-language": "en"
            },
            12,
        )
        a = d.get("address") or {}
        country_code = (a.get("country_code") or "").upper()
        country = a.get("country") or ""
        city = (
            a.get("city") or a.get("town") or a.get("municipality") or
            a.get("village") or a.get("suburb") or a.get("city_district") or ""
        )
        district = a.get("city_district") or a.get("district") or a.get("county") or ""
        province = a.get("state") or a.get("province") or a.get("region") or ""
        return {
            "country_code": country_code,
            "country": country,
            "city": city,
            "district": district,
            "province": province,
        }
    except Exception:
        return {"country_code":"","country":"","city":"","district":"","province":""}

def get_weather(lat, lon):
    params = {
        "latitude":lat, "longitude":lon, "timezone":"auto",
        "temperature_unit":"celsius", "wind_speed_unit":"kmh",
        "forecast_days":7,
        "current":"temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,pressure_msl,wind_speed_10m,wind_direction_10m,cloud_cover,is_day",
        "hourly":"temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,precipitation_probability,weather_code,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover,is_day,cape",
        "daily":"weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,sunrise,sunset,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,uv_index_max,sunshine_duration",
    }
    return request_json(FORECAST_URL, params, 20)

def lightning_risk(code, cape):
    code = int(code or 0)
    cape = float(cape or 0)
    if code >= 95 or cape >= 1000:
        return "high"
    if code >= 80 or cape >= 500:
        return "medium"
    return "low"

def cardinal(deg):
    try:
        d = float(deg) % 360
    except Exception:
        return "—"
    names = ["N","NE","E","SE","S","SW","W","NW"]
    return names[int((d + 22.5)//45) % 8]

class MetevraFletApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.lang = "EN"  # FIRST OPENING IS ENGLISH
        self.t = LANG[self.lang]
        self.lat = None
        self.lon = None
        self.place_name = ""
        self.country_code = ""
        self.weather_data = None
        self.countries = []
        self.provinces = []
        self.districts = []
        self.radar_url = None
        self._geolocator = None
        self.forecast_days = 7

        page.title = self.t["title"]
        page.theme_mode = ft.ThemeMode.DARK
        page.bgcolor = "#07111F"
        page.padding = 0
        page.scroll = ft.ScrollMode.AUTO

        self.location_text = ft.Text("—", size=15, color="#AFC1D8")
        self.temperature = ft.Text("--°", size=64, weight=ft.FontWeight.BOLD)
        self.condition = ft.Text("—", size=20)
        self.sun_text = ft.Text("—", size=14)
        self.details = ft.ResponsiveRow()

        self.country_search = ft.TextField(
            hint_text=self.t["search_country"], prefix_icon=ft.Icons.PUBLIC,
            border_radius=16, on_change=self.filter_countries, expand=True)
        self.country_results = ft.Column(spacing=5, scroll=ft.ScrollMode.AUTO, height=160)

        self.city_search = ft.TextField(
            hint_text=self.t["search_city"], prefix_icon=ft.Icons.SEARCH,
            border_radius=16, on_submit=self.search_city, expand=True)
        self.city_button = ft.IconButton(icon=ft.Icons.SEARCH, on_click=self.search_city)
        self.city_results = ft.Column(spacing=5)

        self.province_dropdown = ft.Dropdown(
            label=self.t["select_province"], width=300, visible=False,
            options=[], on_select=self.select_province)
        self.district_dropdown = ft.Dropdown(
            label=self.t["select_district"], width=300, visible=False,
            options=[], on_select=self.select_district)

        self.location_button = ft.OutlinedButton(
            self.t["find_location"], icon=ft.Icons.MY_LOCATION, on_click=self.use_location)

        self.hourly = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=9)
        self.daily = ft.Column(spacing=7)
        self.forecast_selector = ft.Dropdown(
            label="Forecast",
            value="7",
            width=150,
            options=[
                ft.DropdownOption(key="5", text="5 Days"),
                ft.DropdownOption(key="7", text="7 Days"),
            ],
            on_select=self.change_forecast_days,
        )
        self.status = ft.Text("", size=13)

        self.map = None
        if ftm is not None:
            self.map = ftm.Map(
                expand=True, initial_center=ftm.MapLatitudeLongitude(20,0),
                initial_zoom=2.5,
                layers=[ftm.TileLayer(
                    url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    user_agent_package_name="com.metevra.weather")]
            )

        self.map_type = ft.Dropdown(
            label=self.t["map"], value="road", width=180,
            options=[
                ft.DropdownOption(key="road", text="🗺️ " + self.t["road"]),
                ft.DropdownOption(key="earth", text="🌎 " + self.t["earth"]),
                ft.DropdownOption(key="terrain", text="⛰️ " + self.t["terrain"]),
                ft.DropdownOption(key="radar", text="📡 " + self.t["radar"]),
            ],
            on_select=self.change_map_type)

        self.language_dropdown = ft.Dropdown(
            label=self.t["language"] if "language" in self.t else "Language",
            value="EN",
            options=[ft.DropdownOption(key=k,text=v) for k,v in LANG_NAMES.items()],
            on_select=self.change_language, width=150)

        page.appbar = ft.AppBar(
            title=ft.Text("Metevra Weather", weight=ft.FontWeight.BOLD),
            bgcolor="#0B1A2B", actions=[self.language_dropdown])

        page.add(ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Text("Metevra Weather", size=30, weight=ft.FontWeight.BOLD),
                        ft.Text("Global weather • GPS • 81 il + ilçe • 5/7 days • Radar",
                                size=14, color="#8FA7C2"),
                        ft.Row([self.country_search], spacing=6),
                        self.country_results,
                        ft.Row([self.city_search, self.city_button], spacing=5),
                        self.city_results,
                        ft.Row([self.province_dropdown, self.district_dropdown], wrap=True, spacing=8),
                        self.location_button,
                    ], spacing=10), padding=20),
                self._current_card(),
                self._hourly_card(),
                self._daily_card(),
                self._map_card(),
                ft.Container(self.status, padding=20),
                ft.Text(self.t["source"], size=11, color="#70869D"),
                ft.Text(self.t["radar_source"], size=11, color="#70869D"),
            ], spacing=0), expand=True))

        page.run_task(self.startup)

    def _current_card(self):
        return ft.Container(content=ft.Column([
            self.location_text,
            ft.Row([self.temperature,
                    ft.Column([self.condition, self.sun_text],
                              alignment=ft.MainAxisAlignment.CENTER, spacing=4)],
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
            self.details,
        ], spacing=10), padding=20, margin=ft.Margin.symmetric(horizontal=16),
        border_radius=24, bgcolor="#10243A")

    def _hourly_card(self):
        return ft.Container(content=ft.Column([
            ft.Text(self.t["hourly"], size=20, weight=ft.FontWeight.BOLD),
            self.hourly,
        ], spacing=10), padding=20)

    def _daily_card(self):
        return ft.Container(content=ft.Column([
            ft.Row([ft.Text(self.t["daily"], size=20, weight=ft.FontWeight.BOLD), self.forecast_selector], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            self.daily,
        ], spacing=10), padding=20)

    def _map_card(self):
        map_control = self.map if self.map is not None else ft.Text("flet-map is not installed.")
        return ft.Container(content=ft.Column([
            ft.Row([ft.Text("🗺️ " + self.t["map"], size=20, weight=ft.FontWeight.BOLD),
                    self.map_type], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(content=map_control, height=430, border_radius=18,
                         clip_behavior=ft.ClipBehavior.HARD_EDGE),
        ], spacing=10), padding=20)

    async def startup(self):
        # Country list is the first location/search layer.
        try:
            self.countries = await asyncio.to_thread(get_countries)
            self.render_country_results(self.countries[:300])
        except Exception:
            self.set_status(self.t["network_error"])
        # NOTE: We intentionally do NOT auto-run location detection on
        # startup anymore. On a Windows desktop without GPS hardware,
        # Windows Location Services falls back to Wi-Fi/network-based
        # positioning, which can be just as inaccurate as IP geolocation
        # (e.g. reporting the wrong city entirely). Auto-applying that on
        # every launch silently overwrote the correct city with a wrong
        # one. Now the user picks a city/il-ilçe manually, or presses
        # "Konumumu bul" explicitly knowing the result may be approximate.

    def country_display_name(self, item):
        if self.lang == "EN":
            return item.get("name") or item.get("code")
        trans = item.get("translations") or {}
        # REST Countries translation keys are language-specific.
        key_map = {
            "TR":"tur","DE":"deu","FR":"fra","ES":"spa","IT":"ita","PT":"por",
            "RU":"rus","AR":"ara","ZH":"zho","JA":"jpn","KO":"kor","HI":"hin",
            "ID":"ind","NL":"nld","PL":"pol","SV":"swe","UK":"ukr",
        }
        node = trans.get(key_map.get(self.lang, ""), {})
        return (node.get("common") if isinstance(node, dict) else None) or item.get("name") or item.get("code")

    def render_country_results(self, rows):
        self.country_results.controls.clear()
        for item in rows[:300]:
            code = item["code"]
            name = self.country_display_name(item)
            if code in EXCLUDED_COUNTRY_CODES:
                continue
            self.country_results.controls.append(
                ft.Container(
                    content=ft.TextButton(
                        content=ft.Text(f"{name}  ({code})"),
                        on_click=lambda e, c=code, n=name: self.page.run_task(self.select_country, c, n)),
                    bgcolor="#0E2033", border_radius=10))
        self.page.update()

    def filter_countries(self, e):
        q = (self.country_search.value or "").strip().lower()
        if not q:
            self.render_country_results(self.countries[:300])
            return
        rows = []
        for x in self.countries:
            translations = x.get("translations") or {}
            translated = " ".join(
                str(v.get("common", ""))
                for v in translations.values()
                if isinstance(v, dict)
            )
            name = str(x.get("name") or "")
            code = str(x.get("code") or "")
            if q in name.lower() or q in code.lower() or q in translated.lower():
                rows.append(x)
        self.render_country_results(rows)

    async def select_country(self, code, name):
        if code in EXCLUDED_COUNTRY_CODES:
            return
        self.country_code = code
        self.country_search.value = name
        self.country_results.controls.clear()
        self.city_search.value = ""
        self.city_results.controls.clear()

        is_tr = code == "TR"
        self.province_dropdown.visible = is_tr
        self.district_dropdown.visible = is_tr
        self.province_dropdown.value = None
        self.district_dropdown.value = None
        if is_tr:
            try:
                self.provinces = await asyncio.to_thread(get_turkiye_provinces)
                self.province_dropdown.options = [
                    ft.DropdownOption(key=str(p["id"]), text=p["name"])
                    for p in self.provinces]
                self.district_dropdown.options = []
            except Exception:
                self.set_status(self.t["network_error"])
        self.page.update()

    async def select_province(self, e):
        if not e.control.value:
            return
        try:
            self.districts = await asyncio.to_thread(
                get_turkiye_districts, int(e.control.value))
            self.district_dropdown.options = [
                ft.DropdownOption(key=str(d["id"]), text=d["name"])
                for d in self.districts]
            self.district_dropdown.value = None
            self.district_dropdown.visible = True
            self.page.update()
        except Exception as ex:
            print(f"[DISTRICTS] {ex}")
            self.set_status(self.t["network_error"])

    async def select_district(self, e):
        if not e.control.value:
            return
        district = next((d for d in self.districts if str(d["id"]) == str(e.control.value)), None)
        if not district:
            return
        self.city_search.value = district["name"]
        self.city_results.controls.clear()
        self.set_status(self.t["loading"])
        try:
            lang = self.api_language()
            # Small districts are often missing from the geocoder's index
            # under "District, Türkiye" — try a few query shapes before
            # giving up, and auto-apply the first hit instead of forcing
            # the user to click it again in a results list.
            province_name = next(
                (p["name"] for p in self.provinces if str(p["id"]) == str(district.get("provinceId", ""))),
                "")
            attempts = [district["name"]]
            if province_name:
                attempts.append(f'{district["name"]}, {province_name}')
            attempts.append(f'{district["name"]}, Türkiye')

            results = []
            for q in attempts:
                results = await asyncio.to_thread(geocode_city, q, lang, "TR")
                if results:
                    break
            if not results:
                results = await asyncio.to_thread(geocode_city, district["name"], lang, None)

            if not results:
                print(f"[DISTRICT] no geocoding match for {district['name']!r}")
                self.set_status(self.t["search_error"])
                self.page.update()
                return

            await self.select_result(results[0])
        except Exception as ex:
            print(f"[DISTRICT] {ex}")
            self.set_status(self.t["network_error"])
            self.page.update()

    async def search_city(self, e):
        query = (self.city_search.value or "").strip()
        if len(query) < 2:
            return
        await self.search_and_select(query, self.country_code or None)

    async def search_and_select(self, query, country_code=None):
        self.city_results.controls.clear()
        self.set_status(self.t["loading"])
        try:
            results = await asyncio.to_thread(
                geocode_city, query, self.api_language(), country_code)
            # If a selected-country filter gives no hit, retry globally.
            if not results and country_code:
                results = await asyncio.to_thread(
                    geocode_city, query, self.api_language(), None)
            results = [r for r in results if (r.get("country_code") or "").upper() not in EXCLUDED_COUNTRY_CODES]
            if not results:
                self.set_status(self.t["search_error"])
                self.page.update()
                return
            for item in results[:10]:
                name = item.get("name","")
                region = item.get("admin1","")
                country = item.get("country","")
                label = " • ".join(x for x in [name,region,country] if x)
                self.city_results.controls.append(
                    ft.Container(content=ft.TextButton(
                        content=ft.Text(label), on_click=lambda ev,r=item:self.page.run_task(self.select_result, r)),
                        bgcolor="#0E2033", border_radius=10))
            self.set_status("")
            self.page.update()
        except Exception:
            self.set_status(self.t["network_error"])
            self.page.update()

    async def select_result(self, item):
        self.city_results.controls.clear()
        self.city_search.value = item.get("name","")
        self.lat = float(item["latitude"])
        self.lon = float(item["longitude"])
        self.country_code = (item.get("country_code") or "").upper()
        self.set_language_from_country(self.country_code)
        self.place_name = " • ".join(x for x in [
            item.get("name",""), item.get("admin1",""), item.get("country","")] if x)
        await self.load_weather(self.lat, self.lon, self.place_name)

    async def use_location(self, e):
        self.set_status(self.t["loading"])

        errors = []

        # 1) Windows native Location Services FIRST. This avoids the common
        # desktop problem where an ISP/IP database says the PC is in another
        # city. Windows can use Wi-Fi/GNSS and reports actual accuracy.
        try:
            if wdg is not None:
                lat, lon, accuracy = await asyncio.wait_for(
                    get_windows_location(), timeout=25
                )
                await self.apply_location(lat, lon, accuracy)
                return
            errors.append("Windows Location API yok")
        except Exception as ex:
            errors.append(f"Windows: {ex}")

        # 2) Flet Geolocator as a second native-device method.
        try:
            if ftg is not None:
                self._geolocator = ftg.Geolocator(
                    configuration=ftg.GeolocatorConfiguration(
                        accuracy=ftg.GeolocatorPositionAccuracy.BEST_FOR_NAVIGATION,
                        distance_filter=0,
                    )
                )
                try:
                    await self._geolocator.request_permission()
                except Exception as ex:
                    errors.append(f"Flet izin: {ex}")
                pos = await asyncio.wait_for(
                    self._geolocator.get_current_position(), timeout=15
                )
                lat, lon = float(pos.latitude), float(pos.longitude)
                await self.apply_location(lat, lon)
                return
            errors.append("Flet Geolocator yok")
        except Exception as ex:
            errors.append(f"Flet: {ex}")

        # IMPORTANT: Never silently use IP geolocation. It is not GPS and is
        # exactly what can produce a wrong city such as Atakum/Samsun.
        self.set_status("📍 " + self.t["location_error"])
        print("[LOCATION] " + " | ".join(errors))
        self.page.update()

    async def apply_location(self, lat, lon, accuracy=None):
        """Reverse geocode and apply a device location to the weather UI."""
        lat, lon = float(lat), float(lon)
        loc = await asyncio.to_thread(reverse_location, lat, lon)
        cc = (loc.get("country_code") or "").upper()
        if cc in EXCLUDED_COUNTRY_CODES:
            self.set_status(self.t["location_error"])
            return

        self.lat, self.lon = lat, lon
        self.country_code = cc
        self.set_language_from_country(cc)

        parts = []
        for value in (
            loc.get("city"),
            loc.get("district"),
            loc.get("province"),
            loc.get("country"),
        ):
            if value and value not in parts:
                parts.append(value)

        place = " • ".join(parts) or "Current location"
        # Keep accuracy visible when Windows supplies it; this makes it clear
        # whether the PC received a precise Wi-Fi/GNSS fix or a coarse one.
        if accuracy is not None:
            try:
                accuracy_m = float(accuracy)
                if accuracy_m < 1000:
                    place += f" • ±{accuracy_m:.0f} m"
                else:
                    place += f" • ±{accuracy_m/1000:.1f} km"
            except Exception:
                pass

        await self.load_weather(lat, lon, "📍 " + place)

    def set_language_from_country(self, cc):
        new_lang = COUNTRY_LANGUAGE.get((cc or "").upper(), "EN")
        if new_lang in LANG:
            self.lang = new_lang
            self.t = LANG[new_lang]
            self.language_dropdown.value = new_lang
            self.page.rtl = new_lang == "AR"
            self.refresh_texts()

    async def load_weather(self, lat, lon, place):
        self.set_status(self.t["loading"])
        try:
            self.weather_data = await asyncio.to_thread(get_weather, lat, lon)
            self.place_name = place
            self.render_weather(self.weather_data)
            await self.load_radar()
            await self.update_map(lat, lon)
            self.set_status("")
            self.page.update()
        except Exception:
            self.set_status(self.t["network_error"])
            self.page.update()

    def render_weather(self, data):
        cur = data.get("current", {})
        hourly = data.get("hourly", {})
        daily = data.get("daily", {})

        code = int(cur.get("weather_code") or 0)
        temp = cur.get("temperature_2m")
        apparent = cur.get("apparent_temperature")
        humidity = cur.get("relative_humidity_2m")
        wind = cur.get("wind_speed_10m")
        wind_dir = cur.get("wind_direction_10m")
        pressure = cur.get("pressure_msl")
        precip = cur.get("precipitation")
        cloud = cur.get("cloud_cover")
        is_day = cur.get("is_day")

        self.location_text.value = self.place_name or "—"
        self.temperature.value = f"{temp:.0f}°" if temp is not None else "--°"
        self.condition.value = f"{weather_icon(code)}  {self.code_text(code)}"
        self.sun_text.value = ("☀️ " + self.t["day"] if is_day else "🌙 " + self.t["night"]) + \
                              (f" • {cloud:.0f}% {self.t['cloud']}" if cloud is not None else "")

        # Current lightning risk uses thunderstorm weather code + CAPE.
        cape_now = 0
        times = hourly.get("time", [])
        capes = hourly.get("cape", [])
        if times and capes:
            cape_now = capes[0] or 0
        risk = lightning_risk(code, cape_now)
        risk_label = {"low":self.t["low"],"medium":self.t["medium"],"high":self.t["high"]}[risk]

        self.details.controls = [
            self.detail_card("💧 " + self.t["humidity"], f"{humidity:.0f}%" if humidity is not None else "--"),
            self.detail_card("💨 " + self.t["wind"], f"{wind:.0f} km/h {cardinal(wind_dir)}" if wind is not None else "--"),
            self.detail_card("🌡️ " + self.t["feels"], f"{apparent:.0f}°" if apparent is not None else "--"),
            self.detail_card("🧭 " + self.t["pressure"], f"{pressure:.0f} hPa" if pressure is not None else "--"),
            self.detail_card("🌧️ " + self.t["precip"], f"{precip:.1f} mm" if precip is not None else "--"),
            self.detail_card("⚡ " + self.t["lightning"], risk_label),
        ]

        # 12 hours starting from the current/nearest returned hour.
        self.hourly.controls.clear()
        ht = hourly.get("time", [])
        htemp = hourly.get("temperature_2m", [])
        hcode = hourly.get("weather_code", [])
        hpop = hourly.get("precipitation_probability", [])
        hwind = hourly.get("wind_speed_10m", [])
        hgust = hourly.get("wind_gusts_10m", [])
        hcape = hourly.get("cape", [])
        for i in range(min(12, len(ht))):
            try:
                label = datetime.fromisoformat(ht[i]).strftime("%H:%M")
            except Exception:
                label = ht[i]
            hrisk = lightning_risk(hcode[i] if i < len(hcode) else 0,
                                   hcape[i] if i < len(hcape) else 0)
            self.hourly.controls.append(
                ft.Container(content=ft.Column([
                    ft.Text(label, weight=ft.FontWeight.BOLD),
                    ft.Text(weather_icon(hcode[i] if i < len(hcode) else 0), size=28),
                    ft.Text(f"{htemp[i]:.0f}°" if i < len(htemp) and htemp[i] is not None else "--"),
                    ft.Text(f"💧 {hpop[i]:.0f}%" if i < len(hpop) and hpop[i] is not None else "💧 --"),
                    ft.Text(f"💨 {hwind[i]:.0f}" if i < len(hwind) and hwind[i] is not None else "💨 --"),
                    ft.Text("⚡ " + {"low":self.t["low"],"medium":self.t["medium"],"high":self.t["high"]}[hrisk], size=11),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
                width=105, padding=10, border_radius=16, bgcolor="#10243A")
            )

        # 15 days.
        self.daily.controls.clear()
        dates = daily.get("time", [])
        maxs = daily.get("temperature_2m_max", [])
        mins = daily.get("temperature_2m_min", [])
        dcodes = daily.get("weather_code", [])
        pops = daily.get("precipitation_probability_max", [])
        sunrises = daily.get("sunrise", [])
        sunsets = daily.get("sunset", [])
        wmax = daily.get("wind_speed_10m_max", [])
        gust = daily.get("wind_gusts_10m_max", [])
        uv = daily.get("uv_index_max", [])

        for i in range(min(self.forecast_days, len(dates))):
            try:
                label = datetime.fromisoformat(dates[i]).strftime("%a %d")
            except Exception:
                label = dates[i]
            if i == 0:
                label = self.t["today"]
            row = ft.Container(
                content=ft.Row([
                    ft.Container(ft.Text(label, weight=ft.FontWeight.BOLD), width=80),
                    ft.Text(weather_icon(dcodes[i] if i < len(dcodes) else 0), size=28, width=45),
                    ft.Text(f"{maxs[i]:.0f}° / {mins[i]:.0f}°", width=90),
                    ft.Text(f"💧 {pops[i]:.0f}%" if i < len(pops) and pops[i] is not None else "💧 --", width=70),
                    ft.Text(f"💨 {wmax[i]:.0f}" if i < len(wmax) and wmax[i] is not None else "💨 --", width=70),
                    ft.Text(f"🌅 {self.short_time(sunrises[i])}" if i < len(sunrises) else "🌅 --", width=70),
                    ft.Text(f"🌇 {self.short_time(sunsets[i])}" if i < len(sunsets) else "🌇 --", width=70),
                    ft.Text(f"UV {uv[i]:.0f}" if i < len(uv) and uv[i] is not None else "UV --", width=55),
                ], scroll=ft.ScrollMode.AUTO, spacing=7),
                padding=10, border_radius=12, bgcolor="#10243A")
            self.daily.controls.append(row)

        # Sunrise/sunset are prominent in the current section.
        if sunrises and sunsets:
            self.sun_text.value += f" • 🌅 {self.short_time(sunrises[0])}  🌇 {self.short_time(sunsets[0])}"

    @staticmethod
    def short_time(value):
        if not value:
            return "--"
        try:
            return datetime.fromisoformat(value).strftime("%H:%M")
        except Exception:
            return str(value)[11:16] if len(str(value)) >= 16 else str(value)

    async def load_radar(self):
        # RainViewer current API exposes the latest past radar frame.
        if self.lat is None or self.lon is None:
            return
        try:
            meta = await asyncio.to_thread(
                request_json, "https://api.rainviewer.com/public/weather-maps.json", None, 10)
            frames = ((meta.get("radar") or {}).get("past") or [])
            if frames:
                frame = frames[-1]
                self.radar_url = (
                    f'{meta["host"]}{frame["path"]}/256/{{z}}/{{x}}/{{y}}/2/1_1.png')
        except Exception:
            self.radar_url = None
        self._geolocator = None
        self.forecast_days = 7

    async def update_map(self, lat, lon):
        if self.map is None or ftm is None:
            return
        try:
            await self.map.move_to(ftm.MapLatitudeLongitude(float(lat), float(lon)), zoom=9)
            marker = ftm.Marker(
                coordinates=ftm.MapLatitudeLongitude(float(lat), float(lon)),
                content=ft.Container(content=ft.Icon(ft.Icons.LOCATION_ON, size=36),
                                     width=44, height=44), width=44, height=44)
            base = self.map_tile_for(self.map_type.value or "road")
            layers = [ftm.TileLayer(url_template=base,
                                    user_agent_package_name="com.metevra.weather")]
            if (self.map_type.value or "road") == "radar" and self.radar_url:
                layers.append(ftm.TileLayer(url_template=self.radar_url,
                                            user_agent_package_name="com.metevra.weather"))
            layers.extend([
                ftm.MarkerLayer(markers=[marker]),
                ftm.SimpleAttribution(text="OpenStreetMap / RainViewer")
            ])
            self.map.layers = layers
            await self.page.update_async()
        except Exception:
            pass

    def map_tile_for(self, kind):
        if kind == "earth":
            return "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        if kind == "terrain":
            return "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
        return "https://tile.openstreetmap.org/{z}/{x}/{y}.png"

    def change_map_type(self, e):
        if self.lat is not None:
            self.page.run_task(self.update_map, self.lat, self.lon)

    def api_language(self):
        return {
            "TR":"tr","EN":"en","DE":"de","FR":"fr","ES":"es","IT":"it","PT":"pt",
            "RU":"ru","AR":"ar","ZH":"zh","JA":"ja","KO":"ko","HI":"hi","ID":"id",
            "NL":"nl","PL":"pl","SV":"sv","UK":"uk"
        }.get(self.lang, "en")

    def refresh_texts(self):
        self.country_search.hint_text = self.t["search_country"]
        self.city_search.hint_text = self.t["search_city"]
        try:
            self.location_button.text = self.t["find_location"]
        except Exception:
            try:
                self.location_button.content = self.t["find_location"]
            except Exception:
                pass
        self.province_dropdown.label = self.t["select_province"]
        self.district_dropdown.label = self.t["select_district"]
        self.map_type.label = self.t["map"]
        self.forecast_selector.label = self.t.get("daily", "Forecast")
        self.language_dropdown.value = self.lang
        self.page.title = self.t["title"]
        if self.weather_data:
            self.render_weather(self.weather_data)
        self.page.update()

    def change_forecast_days(self, e):
        try:
            self.forecast_days = 5 if str(e.control.value) == "5" else 7
            self.forecast_selector.value = str(self.forecast_days)
            if self.weather_data:
                self.render_weather(self.weather_data)
                self.page.update()
        except Exception:
            pass

    def change_language(self, e):
        value = e.control.value or "EN"
        if value not in LANG:
            return
        self.lang = value
        self.t = LANG[value]
        self.refresh_texts()

    @staticmethod
    def detail_card(title, value):
        return ft.Container(content=ft.Column([
            ft.Text(title, size=11, color="#8FA7C2"),
            ft.Text(value, size=15, weight=ft.FontWeight.BOLD)
        ], spacing=4), padding=10, border_radius=14,
        bgcolor="#0B1A2B", col={"xs":6,"sm":4,"md":2})

    def code_text(self, code):
        code = int(code or 0)
        labels = {
            "TR": {0:"Açık",1:"Az bulutlu",2:"Parçalı bulutlu",3:"Bulutlu",45:"Sisli",48:"Sisli","rain":"Yağmur","snow":"Kar","storm":"Fırtına","showers":"Sağanak","var":"Değişken"},
            "EN": {0:"Clear",1:"Mainly clear",2:"Partly cloudy",3:"Cloudy",45:"Fog",48:"Fog","rain":"Rain","snow":"Snow","storm":"Thunderstorm","showers":"Showers","var":"Variable"},
            "DE": {0:"Klar",1:"Heiter",2:"Teilweise bewölkt",3:"Bewölkt",45:"Nebel",48:"Nebel","rain":"Regen","snow":"Schnee","storm":"Gewitter","showers":"Schauer","var":"Wechselhaft"},
            "FR": {0:"Dégagé",1:"Peu nuageux",2:"Partiellement nuageux",3:"Nuageux",45:"Brouillard",48:"Brouillard","rain":"Pluie","snow":"Neige","storm":"Orage","showers":"Averses","var":"Variable"},
            "ES": {0:"Despejado",1:"Poco nuboso",2:"Parcialmente nublado",3:"Nublado",45:"Niebla",48:"Niebla","rain":"Lluvia","snow":"Nieve","storm":"Tormenta","showers":"Chubascos","var":"Variable"},
            "IT": {0:"Sereno",1:"Poco nuvoloso",2:"Parzialmente nuvoloso",3:"Nuvoloso",45:"Nebbia",48:"Nebbia","rain":"Pioggia","snow":"Neve","storm":"Temporale","showers":"Rovesci","var":"Variabile"},
            "PT": {0:"Limpo",1:"Pouco nublado",2:"Parcialmente nublado",3:"Nublado",45:"Nevoeiro",48:"Nevoeiro","rain":"Chuva","snow":"Neve","storm":"Trovoada","showers":"Aguaceiros","var":"Variável"},
            "RU": {0:"Ясно",1:"Малооблачно",2:"Переменная облачность",3:"Облачно",45:"Туман",48:"Туман","rain":"Дождь","snow":"Снег","storm":"Гроза","showers":"Ливни","var":"Переменная"},
            "AR": {0:"صافي",1:"غائم قليلاً",2:"غائم جزئياً",3:"غائم",45:"ضباب",48:"ضباب","rain":"مطر","snow":"ثلج","storm":"عاصفة رعدية","showers":"زخات","var":"متغير"},
            "ZH": {0:"晴",1:"晴间多云",2:"局部多云",3:"阴天",45:"雾",48:"雾","rain":"雨","snow":"雪","storm":"雷暴","showers":"阵雨","var":"多变"},
            "JA": {0:"晴れ",1:"晴れ時々曇り",2:"部分的に曇り",3:"曇り",45:"霧",48:"霧","rain":"雨","snow":"雪","storm":"雷雨","showers":"にわか雨","var":"変わりやすい"},
            "KO": {0:"맑음",1:"대체로 맑음",2:"부분 흐림",3:"흐림",45:"안개",48:"안개","rain":"비","snow":"눈","storm":"뇌우","showers":"소나기","var":"변화무쌍"},
            "HI": {0:"साफ",1:"मुख्यतः साफ",2:"आंशिक बादल",3:"बादल",45:"कोहरा",48:"कोहरा","rain":"बारिश","snow":"बर्फ","storm":"आंधी","showers":"बौछार","var":"परिवर्तनशील"},
            "ID": {0:"Cerah",1:"Cerah berawan",2:"Berawan sebagian",3:"Berawan",45:"Kabut",48:"Kabut","rain":"Hujan","snow":"Salju","storm":"Badai petir","showers":"Hujan deras","var":"Berubah"},
            "NL": {0:"Helder",1:"Overwegend helder",2:"Half bewolkt",3:"Bewolkt",45:"Mist",48:"Mist","rain":"Regen","snow":"Sneeuw","storm":"Onweer","showers":"Buien","var":"Wisselvallig"},
            "PL": {0:"Bezchmurnie",1:"Przeważnie pogodnie",2:"Częściowe zachmurzenie",3:"Pochmurno",45:"Mgła",48:"Mgła","rain":"Deszcz","snow":"Śnieg","storm":"Burza","showers":"Przelotne opady","var":"Zmiennie"},
            "SV": {0:"Klart",1:"Mest klart",2:"Delvis molnigt",3:"Molnigt",45:"Dimma",48:"Dimma","rain":"Regn","snow":"Snö","storm":"Åska","showers":"Skurar","var":"Växlande"},
            "UK": {0:"Ясно",1:"Переважно ясно",2:"Мінлива хмарність",3:"Хмарно",45:"Туман",48:"Туман","rain":"Дощ","snow":"Сніг","storm":"Гроза","showers":"Зливи","var":"Мінливо"},
        }
        l = labels.get(self.lang, labels["EN"])
        if code in (0,1,2,3,45,48):
            return l[code]
        if code >= 95: return l["storm"]
        if code >= 80: return l["showers"]
        if code >= 71: return l["snow"]
        if code >= 51: return l["rain"]
        return l["var"]

    def set_status(self, text):
        self.status.value = text
        try:
            self.page.update()
        except Exception:
            pass

def main(page: ft.Page):
    MetevraFletApp(page)

if __name__ == "__main__":
    ft.run(main)
