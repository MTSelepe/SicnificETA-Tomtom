import requests
import json
from datetime import timedelta
import geocoder


""" File contains optimisation code which is run when optimisation is called.
    'geocodes_from_addresses' gets geocodes from a list of addresses.
    'get_optimised_route' uses waypoint geocodes to find optimised routes.
"""


def to_json(orderid_list, address_list, etas, route,route2,points):
    """ Converts dictionary of outputs to JSON """
    # creates a dictionary with output data
    json_object = {"ordered_orderids": orderid_list, "eta_list": etas, "ordered_addresses": address_list,
                   "route": route,"route2":route2,"points":points}
    # print(json.dumps(json_object, indent=4))
    return json.dumps(json_object, indent=4)


def geocodes_from_addresses_mapbox(addresse_geo, API_key): 
    """ convert addresses to latitude and longitude
        Mapbox Api
    """
    
    geocodes = []
    tomtom_geocodes = ""
    lat = ""
    long = ""
    g_API_key = "AIzaSyCNSyD13siR0AvcuoKMBntWw_b0xz_n_AQ" # google api
    for address in addresse_geo:
        g = geocoder.mapbox(address, key=API_key) # mapbox api to convert address to latitude and longitude
        r = g.json
        if g.ok == False:    # if mapbox fail consider google api
            g = geocoder.google(address, key=g_API_key) # google api to convert address to latitude and longitude
            r = g.json
            if g.ok == False:   # if google api fail return error message
                print(g.status,g.location)
            else:
                lat = r["lat"]
                long = r["lng"]
        else:
            lat = r["lat"]
            long = r["lng"]
                    
        geocodes.append([lat, long])
        tomtom_geocodes += "{},{}:".format(lat, long)
    
    return geocodes, tomtom_geocodes # everything is Ok return results


# def geocodes_from_addresses(addresses_geo, API_key_google_geo):
#     geocodes = []
#     tomtom_geocodes = ""

#     for address in addresses_geo:
#         url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}' \
#               '&key={}'.format(address.replace(' ', '+'), API_key_google_geo)
#         response = requests.get(url)
#         resp_json_payload = response.json()
#         lat = resp_json_payload['results'][0]['geometry']['location']['lat']
#         long = resp_json_payload['results'][0]['geometry']['location']['lng']
#         geocodes.append([lat, long])
#         tomtom_geocodes += "{},{}:".format(lat, long)
#     tomtom_geocodes = tomtom_geocodes.rstrip(":")

#     return geocodes, tomtom_geocodes

def create_route(myObject): 
    """

    find consecutive route from location to location

    """
    route=[]
    for idx in range(len(myObject)):
      leg_latlong = []
      for j in range(len(myObject[idx]["points"])):
         lat = myObject[idx]["points"][j]["latitude"]
         long = myObject[idx]["points"][j]["longitude"]
         leg_latlong.append([lat, long])
      route.append(leg_latlong)
    return route

def create_route2(myObject):
     """
    find longtude and latude between two location 
    
    """
    leg_latlong = []
    for idx in range(len(myObject)):
      
      for j in range(len(myObject[idx]["points"])):
         lat = myObject[idx]["points"][j]["latitude"]
         long = myObject[idx]["points"][j]["longitude"]
         leg_latlong.append([long, lat])
    
    return leg_latlong

def create_route3(myObject):    # exclude logitude and latitude between locations
     """
    find longtude and latude between two location 
    """
    route=[]
    for idx in range(len(myObject)):
      leg_latlong = []
      for j in range(len(myObject[idx]["points"])):
         lat = myObject[idx]["points"][j]["latitude"]
         long = myObject[idx]["points"][j]["longitude"]
         leg_latlong.append([long, lat])
      route.append(leg_latlong[0])
    return route


def get_optimised_route(orderid_list, address_list, API_key_tomtom, API_key_mapbox, start_datetime):

    
    """
    get optimiised route from tomtom solver
    """

    url = ("https://api.tomtom.com/routing/1/calculateRoute/{}/json?instructionsType=text&computeBestOrder=true&"
           "routeRepresentation=polyline&computeTravelTimeFor=all&routeType=fastest&traffic=true&avoid=unpavedRoads"
           "&vehicleEngineType=combustion"
           "&key={}").format(geocodes_from_addresses_mapbox(address_list, API_key_mapbox)[1], API_key_tomtom)
    
    r = requests.get(url)     # request tomtom optimization
    json_response = r.json()  #convert resonse to json object
    
    if r.status_code != 200:  # if their is an error return it
       try:
            print(json_response["error"]["description"])
            return
       except:
            print("Something Went Wrong")    
    
    
    
    # json_response = r.json()

    optimizedWaypoints = [0]
    ETA = [str(start_datetime)[11:19]]
    distance = [0]
    

    for j in range(len(address_list) - 2):
        waypoint = json_response["optimizedWaypoints"][j]["optimizedIndex"]
        optimizedWaypoints.append(waypoint + 1)
    optimizedWaypoints.append(0)

    ordered_addresses = [address_list[i] for i in optimizedWaypoints]  # swap addresses according to optimizide route
    ordered_orderid = [orderid_list[i] for i in optimizedWaypoints]  # swap id's according to optimizide route

    instructions = json_response["routes"][0]["guidance"]["instructions"] 

    for i, val in enumerate(instructions): # retrieve ETA from the response 
        if "reached the waypoint" in val["message"]:
            ETA.append(str(start_datetime + timedelta(seconds=val["travelTimeInSeconds"]))[11:19])
            distance.append(val["routeOffsetInMeters"])
    end_time = instructions[len(instructions)-1]["travelTimeInSeconds"]
    end_distance = instructions[len(instructions)-1]["routeOffsetInMeters"]
    ETA.append(str(start_datetime + timedelta(seconds=end_time))[11:19])
    distance.append(end_distance)

    legs = json_response["routes"][0]["legs"]
    final_route = create_route(legs)
    final_route2 = create_route2(legs)
    points = create_route3(legs)
    

    return to_json(ordered_orderid, ordered_addresses, ETA, final_route,final_route2,points)

