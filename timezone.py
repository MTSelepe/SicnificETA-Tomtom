import pytz
import urllib.request
from datetime import datetime, timedelta
import json


def get_timezone(address_list, API_key):

  timestamp = datetime.now().timestamp()
  utc_values = []

  utc_virginia = '0000'
  utc_values.append(utc_virginia)

  ###              get coordinates from address               ###
  coord_request = 'https://maps.googleapis.com/maps/api/geocode/json?'
  coord_request += 'address={}&key={}'.format(address_list[0].replace(" ", "+"), API_key)
  # logging.warning(coord_request)

  jsonResult = urllib.request.urlopen(coord_request).read()
  coord_response = json.loads(jsonResult)

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