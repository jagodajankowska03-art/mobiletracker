from flask import Flask, render_template, request
import requests
app = Flask(__name__, static_folder='.', template_folder='.')
GOOGLE_API_KEY = "TWOJ_KLUCZ_API"  # wklej swój klucz Google Maps API
def get_distance(origin, destination):
    """Odległość w metrach między dwoma adresami"""
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&key={GOOGLE_API_KEY}"
    try:
        resp = requests.get(url).json()
        return resp['rows'][0]['elements'][0]['distance']['value']
    except:
        return float('inf')
def nearest_neighbor_split(addresses):
    """Szybki podział adresów między 2 kierowców używając algorytmu najbliższego sąsiada"""
    if len(addresses) < 2:
        return addresses, []
    start_a = addresses[0]  # start kierowcy A
    start_b = addresses[-1] # start kierowcy B
    remaining = set(addresses[1:-1])
    route_a = [start_a]
    route_b = [start_b]
    while remaining:
        next_addr = min(remaining, key=lambda x: min(get_distance(route_a[-1], x), get_distance(route_b[-1], x)))
        # przypisz do kierowcy bliższego
        if get_distance(route_a[-1], next_addr) <= get_distance(route_b[-1], next_addr):
            route_a.append(next_addr)
        else:
            route_b.append(next_addr)
        remaining.remove(next_addr)
    return route_a, route_b
def generate_url(addresses):
    """Tworzy link Google Maps dla listy adresów"""
    if len(addresses) < 2:
        return ""
    base = "https://www.google.com/maps/dir/?api=1"
    origin = addresses[0]
    destination = addresses[-1]
    waypoints = "|".join(addresses[1:-1]) if len(addresses) > 2 else ""
    url = f"{base}&origin={origin}&destination={destination}&travelmode=driving"
    if waypoints:
        url += f"&waypoints={waypoints}"
    return url
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        addresses = request.form.get("addresses")
        addresses_list = [a.strip() for a in addresses.split("\n") if a.strip()]
        if len(addresses_list) < 2:
            return render_template("index.html", error="Wpisz co najmniej dwa adresy.")
        route_a, route_b = nearest_neighbor_split(addresses_list)
        url_a = generate_url(route_a)
        url_b = generate_url(route_b)
        return render_template("index.html", results=[("Kierowca A", url_a), ("Kierowca B", url_b)])
    return render_template("index.html")
