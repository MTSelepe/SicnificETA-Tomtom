import urllib.request
from datetime import datetime, timedelta
import json
import geocoder
import requests
import pytz



def get_timezone(address_list, API_key):   # to timezone
    """ get timezone of depot addresses time"""
    
    timestamp = datetime.now().timestamp()
    utc_values = []

    utc_virginia = '0000'
    utc_values.append(utc_virginia)

    ###              get coordinates from address               ###
    coord_request = 'https://maps.googleapis.com/maps/api/geocode/json?'
    coord_request += 'address={}&key={}'.format(address_list[0], API_key)
    # logging.warning(coord_request)

    jsonResult = urllib.request.urlopen(coord_request).read()
    coord_response = json.loads(jsonResult)
    # print(coord_response)

    # latitude and longitude components
    latitude = coord_response['results'][0]['geometry']['location']['lat']
    longitude = coord_response['results'][0]['geometry']['location']['lng']


    timezone_request = 'https://maps.googleapis.com/maps/api/timezone/json?location='
    timezone_request += "{},{}&timestamp={}&key={}".format(latitude, longitude, timestamp, API_key)

    jsonResult = urllib.request.urlopen(timezone_request).read()
    coord_response = json.loads(jsonResult)
    timezone_id = coord_response['timeZoneId']

    utc = datetime.now(pytz.timezone(timezone_id)).strftime('%z')
    utc_values.append(utc)

    seconds_dif = []

    for utc_val in utc_values:
        sign = utc_val[0]
        hours = int(utc_val[1:3])
        minutes = int(utc_val[3:5])
        seconds = hours * 3600 + minutes * 60
        if sign == "+":
          seconds *= 1
        else:
          seconds *= -1
       
        seconds_dif.append(seconds)
        

    difference_value = seconds_dif[1] - seconds_dif[0]

    start_time = datetime.now() + timedelta(seconds=difference_value)

    return start_time

def string_of_addrress(addr_element,API_key):
    """ Converts address to langitude and latitude using mapbax api """

    lng_tat = ''
    g = geocoder.mapbox(addr_element,key = API_key)
    g=g.json
    lat=g['lat']
    lng=g['lng']
    lng_tat = str(lat) + ',' + str(lng)

    return lng_tat

def send_request(data_matrix, API_key):

    headers = {
        'Content-type': 'application/json',
    }

    instruct = 'computeBestOrder=true&'\
        'vehicleHeading=90&'\
        'sectionType=traffic&'\
        'routeRepresentation=polyline&'\
        'computeTravelTimeFor=all&'\
        'report=effectiveSettings&'\
        'instructionsType=text&'\
        'routeType=fastest&'\
        'traffic=true&'\
        'avoid=unpavedRoads&'\
        'travelMode=car&'\
        'vehicleMaxSpeed=120&'\
        'key='

    request = requests.get('https://api.tomtom.com/routing/1/calculateRoute/' + data_matrix + '/json?'+ instruct + API_key, headers=headers)
    json_response = request.json()
    
    if request.status_code != 200:
        try:
            print(json_response["error"]["description"])
            return
        except:
            print("Something Went Wrong")    
    
    return request


def single_trip_Time(addr_matrix,API_key):
  MyTime = 0

  Json_response = send_request(addr_matrix , API_key)
  Json_response=json.loads(Json_response.text)

  for Myobject in Json_response['routes'][0]['guidance']['instructions']:

    if 'You have reached the waypoint' in Myobject['message'] or 'You have arrived' in Myobject['message'] :

        trip_time = timedelta(seconds=int(Myobject['travelTimeInSeconds']))
        MyTime =  trip_time


  return MyTime


# def single_trip_eta(origin_addresses, dest_addresses, API_key, departure_time):
#     """ Build and send request for the given origin and destination addresses."""

#     request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
#     traffic_model = 'best_guess'
#     origin_addresses = origin_addresses.replace(" ", "+")
#     dest_addresses = dest_addresses.replace(" ", "+")
#     request = request + '&origins=' + origin_addresses + '&destinations=' + \
#               dest_addresses + '&traffic_model=' + traffic_model +\
#               '&departure_time=' + departure_time + '&key=' + API_key
#     jsonResult = urllib.request.urlopen(request).read()
#     response = json.loads(jsonResult)

#     for row in response['rows']:
#         duration_in_traffic = [row['elements'][j]['duration_in_traffic']['value'] for j in range(len(row['elements']))]

#     return duration_in_traffic[0]


def to_json(orderid_list, address_list, etas):
    """ Converts dictionary of outputs to JSON """
    # creates a dictionary with output data
    json_object = {"ordered_orderids": orderid_list, "eta_list": etas, "ordered_addresses": address_list}
    return json.dumps(json_object, indent=4)


# def get_output_variables_without_optimisation(orderid_list, addresses_list, API_key_google, start_datetime):
#     address_list, eta_list = [], []
#     total_travel_time, stop_time, route_distance = 0, 0, 0
#     eta_list.append(start_datetime.strftime("%H:%M:%S"))
#     a=0
#     for i in range(len(addresses_list)-1):
#         trip_time = single_trip_eta(addresses_list[i], addresses_list[i+1], API_key_google,
#                                     str(int((start_datetime + timedelta(days=14)).timestamp())))
#         total_travel_time += (trip_time + stop_time)
#         eta = str(start_datetime + timedelta(seconds=total_travel_time))
#         address_list.append(addresses_list[i])
#         a += 1
#         eta_list.append(eta[11:19])  # add time portion of eta to output list
    
#     address_list.append(addresses_list[a])
#     return to_json(orderid_list, address_list, eta_list)
