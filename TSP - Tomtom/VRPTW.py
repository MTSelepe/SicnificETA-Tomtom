from __future__ import division
from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
import sys
from datetime import datetime, timedelta

import json
import urllib.request
import pytz
import logging




def resDatas(datas):

 mydatt = datas.split(',')

 return mydatt

def resData(datas):

 mydatt = datas.split(',')

 return mydatt

def create_data():
  """Creates the data."""
  data = {}

  data["API_key"] = "AIzaSyCNSyD13siR0AvcuoKMBntWw_b0xz_n_AQ" # depot
  data["addresses"] = resDatas(sys.argv[3])
  # logging.warning('the entry point for addresses')
  # logging.warning(data['addresses'])


  return data



def MydataF():

  myData=create_data()
  myData=myData["addresses"]


  return myData






def create_distance_matrix(data):
  addresses = data["addresses"]
  # logging.warning('addresses to follow')
  # logging.warning(addresses)
  API_key = data["API_key"]
  # Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
  max_elements = 100
  num_addresses = len(addresses) # 16 in this example.
  # Maximum number of rows that can be computed per request (6 in this example).
  max_rows = max_elements // num_addresses
  # num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
  q, r = divmod(num_addresses, max_rows)
  dest_addresses = addresses
  distance_matrix = []
  # Send q requests, returning max_rows rows per request.
  for i in range(q):
    origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
    # logging.warning('lets see if this works')
    response = send_request(origin_addresses, dest_addresses, API_key)
    distance_matrix += build_distance_matrix(response)

  # Get the remaining remaining r rows, if necessary.
  if r > 0:
    origin_addresses = addresses[q * max_rows: q * max_rows + r]
    # logging.warning('lets see if this works')
    response = send_request(origin_addresses, dest_addresses, API_key)
    distance_matrix += build_distance_matrix(response)
  return distance_matrix

def send_request(origin_addresses, dest_addresses, API_key):
  """ Build and send request for the given origin and destination addresses."""
  def build_address_str(addresses):
    # Build a pipe-separated string of addresses
    address_str = ""
    for i in range(len(addresses) - 1):
      address_str += addresses[i] + "|"
    address_str += addresses[-1]
    return address_str

  request = "https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial"
  origin_address_str = build_address_str(origin_addresses)
  dest_address_str = build_address_str(dest_addresses)

  request = request + "&origins=" + origin_address_str + "&destinations=" + \
                    dest_address_str +"&departure_time=now" +"&traffic_model="+"best_guess"+"&key=" + API_key
  # logging.warning(request)

  jsonResult = urllib.request.urlopen(request).read()
  response = json.loads(jsonResult)
  return response
# duration_in_traffic
def build_distance_matrix(response):
  distance_matrix = []
  dist_matrix=[]
  for row in response["rows"]:
    row_list = [row["elements"][j]["duration_in_traffic"]["value"] for j in range(len(row["elements"]))]
    distance_matrix.append(row_list)
  # for row in response["rows"]:
  #   row_list = [row["elements"][j]["distance"]["value"] for j in range(len(row["elements"]))]
  #   dist_matrix.append(row_list)
  return distance_matrix


########
# Main #
########
def My_distance_matrix():
  """Entry point of the program"""
  # Create the data.
  data = create_data()
  addresses = data["addresses"]
  # logging.warning("addresses from another function")
  # logging.warning(addresses)
  API_key = data["API_key"]
  distance_matrix = create_distance_matrix(data)

  return distance_matrix

myDM=np.array(My_distance_matrix())





def Update_Time_Window_M(dat,Matrx_Data): # update the Time_window() according to order priority





  r=0

  i = 0    # switch between first row and the rest of rows

  for y in dat: # for each position in the array dat

    for x in range(len(Matrx_Data)):


      if x==y and i==0:             # for first row ---- and 1 update
        i=i+1                       # switch to else if statement
        r   = int(myDM[0][x])       # assign r-maximum to the value of position y in time matrix
        l   = Matrx_Data[x][0]      # assign l-minimum to zero
        Matrx_Data[x]=(l,r)         # replace tuple in position x in time_window matrix by new updated tuple



      elif x==y and i != 0:         # for the rest of rows ----- and more than one update

        r   = int(myDM[dat[i-1]][dat[i]]) + r  # addition of path in time matrix
        l   = Matrx_Data[x][0]       # assign l-minimum to zero
        Matrx_Data[x]=(l,r)          # replace tuple in position x in time_window matrix by new updated tuple
        i=i+1

  return Matrx_Data   # return updated time window matrix









def Time_window():  # create time_window_matrix from time_matrix

   max_value=0
   hold_matrix=[]
   for x in range(len(myDM[0, :])):
      max_value= max_value + int(max(myDM[x, :])) # addition of maximum values of each row
      hold_matrix.append(max_value)               # increase size of hold matrix by 1
   DUE_DATE   = [max_value for x in hold_matrix]  # create a list of maximum values
   READY_TIME = [0  for x in hold_matrix]         # create a list of zeros as minimum values
   MyTWData=list(zip(READY_TIME,DUE_DATE))        # create a list of tuple e.g [(a,b),(c,d)]

   return MyTWData


def convert(n):
    return str(timedelta(seconds= n))





def create_data_model():
  """Stores the data for the problem."""



  data = {}


  data['time_matrix']  = myDM
  data['time_windows'] = Update_Time_Window_M(resData(sys.argv[1]),Time_window())
  data['num_vehicles'] = 1
  data['depot'] = 0


  return data


def get_timezone_backup(data):

    timestamp = datetime.now().timestamp()
    utc_values = []

    utc_virginia = '0000'
    utc_values.append(utc_virginia)

    ###              get coordinates from address               ###
    coord_request = 'https://maps.googleapis.com/maps/api/geocode/json?'
    coord_request += 'address={}&key={}'.format(data["addresses"][0], data["API_key"])

    jsonResult = urllib.request.urlopen(coord_request).read()
    coord_response = json.loads(jsonResult)

    # latitude and longitude components
    latitude = coord_response['results'][0]['geometry']['location']['lat']
    longitude = coord_response['results'][0]['geometry']['location']['lng']


    timezone_request = 'https://maps.googleapis.com/maps/api/timezone/json?location='
    timezone_request += "{},{}&timestamp={}&key={}".format(latitude, longitude, timestamp, data["API_key"])

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
        # seconds = str(timedelta(seconds=))
        seconds_dif.append(seconds)
        # print(seconds)

    difference_value = seconds_dif[1] - seconds_dif[0]

    start_time = datetime.now() + timedelta(seconds=difference_value)

    return start_time


def get_timezone(address_list, API_key):

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
        # seconds = str(timedelta(seconds=))
        seconds_dif.append(seconds)
        # print(seconds)

    difference_value = seconds_dif[1] - seconds_dif[0]

    start_time = datetime.now() + timedelta(seconds=difference_value)

    return start_time


def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    time_dimension = routing.GetDimensionOrDie('Time')
    My_matrix_for_everything=[]
    total_time = 0
    time_tracker = 0                # in seconds
    stop_time=int(sys.argv[2])                       # duration for each vehicle in each location
    MyTimes = []                       # matrix for holding time it takes to move from deport to initial destination
    needed_matrx=[]                    # matrix for holding path addresses in needed order
    myIDs=resData(sys.argv[4])
    needed_matrxID = []                # matrix for holding path addresses in needed order
    ETA=[]
    myData = MydataF()
    API_Key = "AIzaSyCNSyD13siR0AvcuoKMBntWw_b0xz_n_AQ"

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        while not routing.IsEnd(index):
            time_var = time_dimension.CumulVar(index)

            if assignment.Min(time_var)==0:

              plan_output += '{0} Time({1},{2}) -> '.format(
                manager.IndexToNode(index), assignment.Min(time_var),
                assignment.Max(time_var)+time_tracker)

              MyTimes.append(assignment.Min(time_var))


              ETA.append( ((get_timezone(myData, API_Key) + timedelta(seconds=(assignment.Min(time_var)))).time()).strftime("%H:%M:%S"))

              needed_matrx.append(myData [manager.IndexToNode(index)])
              needed_matrxID.append(myIDs[manager.IndexToNode(index)])

            else:
              plan_output += '{0} Time({1},{2}) -> '.format(
                manager.IndexToNode(index), assignment.Min(time_var)+time_tracker-stop_time,
                assignment.Max(time_var)+time_tracker)

              MyTimes.append(convert(assignment.Min(time_var)+time_tracker-stop_time))

              ETA.append(((get_timezone(myData, API_Key) + timedelta(seconds=(assignment.Min(time_var)+time_tracker-stop_time))).time()).strftime("%H:%M:%S"))
              needed_matrx.append(myData [manager.IndexToNode(index)])
              needed_matrxID.append(myIDs[manager.IndexToNode(index)])

            time_tracker=time_tracker+stop_time
            index = assignment.Value(routing.NextVar(index))
        time_var = time_dimension.CumulVar(index)

        plan_output += '{0} Time({1},{2})\n'.format(
            manager.IndexToNode(index), assignment.Min(time_var)+time_tracker-stop_time,
                assignment.Max(time_var)+time_tracker)

        MyTimes.append(convert(assignment.Min(time_var)+time_tracker-stop_time))
        ETA.append(((get_timezone(myData, API_Key) + timedelta(seconds=(assignment.Min(time_var)+time_tracker-stop_time))).time()).strftime("%H:%M:%S"))
        needed_matrx.append(myData[manager.IndexToNode(index)])
        needed_matrxID.append(myIDs[manager.IndexToNode(index)])

        plan_output += 'Time of the route: {}sec\n'.format(
            assignment.Min(time_var) + time_tracker )




        My_matrix_for_everything.append(needed_matrx)
        My_matrix_for_everything.append(needed_matrxID)
        My_matrix_for_everything.append(ETA)
        My_matrix_for_everything.append(MyTimes)



        total_time += assignment.Min(time_var)
    My_matrix_for_everything.append('Time of the route: {}'.format( timedelta(seconds=(total_time + time_tracker)) ))
    print(My_matrix_for_everything)


def main():
    """Solve the VRP with time windows."""

    data = create_data_model()                     # pass the input into create_data_fuction


    manager = pywrapcp.RoutingIndexManager(
        len(data['time_matrix']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        """Returns the travel time between the two nodes."""
        # Convert from routing variable Index to time matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    time = 'Time'
    routing.AddDimension(
        transit_callback_index,
        3000000,  # allow waiting time
        1800000,  # maximum time per vehicle
        True,  # Don't force start cumul to zero.
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    # Add time window constraints for each location except depot.
    for location_idx, time_window in enumerate(data['time_windows']):
        if location_idx == 0:
            continue
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
    # Add time window constraints for each vehicle start node.
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        time_dimension.CumulVar(index).SetRange(data['time_windows'][0][0],
                                                data['time_windows'][0][1])
    for i in range(data['num_vehicles']):
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.Start(i)))
        routing.AddVariableMinimizedByFinalizer(
            time_dimension.CumulVar(routing.End(i)))
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    assignment = routing.SolveWithParameters(search_parameters)

    if assignment:
        print_solution(data, manager, routing, assignment)

if __name__ == '__main__':
  main()
