import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import folium
from opencage.geocoder import OpenCageGeocode
from flask import Flask, request, render_template_string

app = Flask(__name__)
GEOAPIFY_KEY = "890d553b870f4ff18daa76b52b6a6518"
LOCATIONIQ_KEY = "pk.eyJ1Ijoiam9obmRvZSIsImEiOiJja3Y3Z3Y3b3YwMDF2MnBtbGZ1ZzZ6N3o0In0.4X5Z5bX5Z5bX5Z5bX5Z5bX5"
key = "f7a14f2afba2457ca65053393b5375ce"  # Your API key


def get_location_data(phone_number):
    parsed_number = phonenumbers.parse(phone_number)

    # Basic number info
    location = geocoder.description_for_number(parsed_number, "en")
    provider = carrier.name_for_number(parsed_number, "en")
    timezones = timezone.time_zones_for_number(parsed_number)
    line_type = phonenumbers.number_type(parsed_number)

    # Convert line type to text
    type_map = {
        phonenumbers.PhoneNumberType.MOBILE: "Mobile",
        phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed/Mobile",
        phonenumbers.PhoneNumberType.VOIP: "VoIP",
        phonenumbers.PhoneNumberType.UNKNOWN: "Unknown"
    }
    line_type_text = type_map.get(line_type, "Unknown")

    # Geocoding for map (city-level)
    geocoder_api = OpenCageGeocode(key)
    results = geocoder_api.geocode(location)
    lat = results[0]['geometry']['lat']
    lng = results[0]['geometry']['lng']

    return {
        "location": location,
        "provider": provider,
        "timezones": timezones,
        "line_type": line_type_text,
        "lat": lat,
        "lng": lng
    }


template = """
<!DOCTYPE html>
<html>
<head>
    <title>Phone Locator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f0f2f5;
            padding: 0;
            margin: 0;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }

        .container {
            width: 90%;
            max-width: 650px;
            background: white;
            margin-top: 40px;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }

        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 25px;
        }

        input {
            width: 100%;
            padding: 14px;
            font-size: 16px;
            border: 1px solid #ccc;
            border-radius: 12px;
            margin-bottom: 15px;
        }

        button {
            width: 100%;
            padding: 14px;
            background: #0066ff;
            color: white;
            font-size: 17px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
        }

        .info-card {
            background: #f7f9fc;
            padding: 15px;
            border-radius: 12px;
            margin-top: 20px;
            border-left: 4px solid #0066ff;
        }

        .info-card p {
            font-size: 16px;
            margin: 8px 0;
        }

        .map-container {
            margin-top: 20px;
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>📍 Phone Number Locator</h1>

        <form method="POST">
            <input type="text" name="phone_number" placeholder="Enter phone e.g. 9876543210" required>
            <button type="submit">Search</button>
        </form>

        {% if details %}
            <div class="info-card">
                <p><strong>📍Number:</strong> {{ phone_number }}</p>
                <p><strong>📡Location:</strong> {{ details.location }}</p>
                <p><strong>🕒Service Provider:</strong> {{ details.provider }}</p>
                <p><strong>🔌Timezone(s):</strong> {{ details.timezones }}</p>
                <p><strong>📞Line Type:</strong> {{ details.line_type }}</p>
                <p><strong>🗺️Latitude:</strong> {{ details.lat }}</p>
                <p><strong>🗺️Longitude:</strong> {{ details.lng }}</p>
            </div>

            <div class="map-container">
                {{ map_html|safe }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        phone_number = request.form.get('phone_number')

        # ⭐ Auto-add + if missing
        if not phone_number.startswith("+"):
            phone_number = "+" + phone_number

        details = get_location_data(phone_number)

        # Create map
        map_instance = folium.Map(location=[details["lat"], details["lng"]], zoom_start=10)
        folium.Marker([details["lat"], details["lng"]], popup=details["location"]).add_to(map_instance)
        map_html = map_instance._repr_html_()

        return render_template_string(template,
                                      phone_number=phone_number,
                                      details=details,
                                      map_html=map_html)

    return render_template_string(template)


if __name__ == "__main__":
    app.run(debug=True)
