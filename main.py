from flask import Flask, request
import folium
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
app = Flask(__name__)
START_ADDRESS = "ul. Ekologiczna 12, 05-080 Klaudyn"
geolocator = Nominatim(user_agent="route_optimizer")
def geocode(address):
    loc = geolocator.geocode(address)
    if loc:
        return (loc.latitude, loc.longitude)
    return (0,0)
# Algorytm nearest neighbor dla jednej trasy
def nearest_neighbor_route(start, addresses):
    route = [start]
    remaining = addresses.copy()
    current = start
    while remaining:
        nearest = min(remaining, key=lambda addr: geodesic(geocode(current), geocode(addr)).km)
        route.append(nearest)
        current = nearest
        remaining.remove(nearest)
    return route
# Dzielimy adresy między kierowców (proporcjonalnie do ilości)
def split_optimized_routes(addresses, num_drivers):
    routes = [[] for _ in range(num_drivers)]
    addresses_copy = addresses.copy()
    for i, addr in enumerate(addresses_copy):
        routes[i % num_drivers].append(addr)
    optimized_routes = [nearest_neighbor_route(START_ADDRESS, r) for r in routes]
    return optimized_routes
COLORS = ["blue", "red", "green", "purple", "orange", "darkred", "cadetblue", "pink"]
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        addresses = [a.strip() for a in request.form.get("addresses").split("\n") if a.strip()]
        num_drivers = int(request.form.get("num_drivers", 2))
        routes = split_optimized_routes(addresses, num_drivers)
        m = folium.Map(location=geocode(START_ADDRESS), zoom_start=11)
        for i, route in enumerate(routes):
            folium.PolyLine([geocode(addr) for addr in route], color=COLORS[i % len(COLORS)], weight=5).add_to(m)
            for addr in route:
                folium.Marker(location=geocode(addr), popup=addr, icon=folium.Icon(color=COLORS[i % len(COLORS)])).add_to(m)
        return m._repr_html_()
    return '''
        <h2>Optymalizacja tras dla kierowców</h2>
        <form method="post">
            Liczba kierowców: <input type="number" name="num_drivers" value="2" min="1" max="8"><br><br>
            Wprowadź adresy (po jednym w wierszu):<br>
            <textarea name="addresses" rows="10" cols="50"></textarea><br><br>
            <input type="submit" value="Generuj trasy">
        </form>
    '''
if __name__ == "__main__":
    app.run(debug=True)
