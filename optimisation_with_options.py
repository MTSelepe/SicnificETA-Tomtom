# main file
import option1_optimisation     # for optimisation
import option2_onlyETA          # for EAT only
import json
import timezone
import sys

""" This is the main file ,it goes hand in hand with option1_optimisation and option2_onlyETA file.
    'The file is connected to node.js.'
    'it receives the following values from node.js file:'
    'sys.argv[3] =  addresses'  
    'sys.argv[4] =  id's '
    'sys.argv[5] =  1 or 2 '  
"""



def resDatas(datas):    # methods to Split a string into an array of substrings

 mydatt = datas.split(',')

 return mydatt

# sys.argv[3] = "address1,address2,......,address(n)"  
# sys.argv[4] = "id1,id2,......,id(n)"     
# sys.argv[5] =  "1" or "2" 

addresses = resDatas(sys.argv[3])  # Split a string into an array of substrings
# addresses = [address1,address2,......,address(n)]


# for optimization solver to work , 
# starting address must be the same as the ending addressa
ad_dres = addresses[0]  # take first address  from 'addresses' array
addresses.append(ad_dres) # add first address to the end of 'addresses' array

order_id = resDatas(sys.argv[4]) # Split a string into an array of substrings
# order_id = [id1,id2,......,id(n)]

API_Key_Google = 'AIzaSyCNSyD13siR0AvcuoKMBntWw_b0xz_n_AQ'     # google api
API_Key_Tomtom = 'cntu9IDdS7Rawt7yAARx9YfxRD7jR4vI'  # tomomt api
API_Key_Mapbox = 'pk.eyJ1Ijoic2lnbmlmaWMiLCJhIjoiY2p6OXVqbzV4MDE2MDNkbzA3bWFuMjBtNiJ9._5hiEwXhS7enZFm_SvmVeg' # mapbox api
optimise_selection = int(sys.argv[5]) # cast to integer 

start_datetime = timezone.get_timezone(addresses, API_Key_Google)


def optimise_or_onlyETA(orderid_list, address_list, optimise, start_datetime):

    if optimise == 1:
        # call optimise function
       
        optimisation_results = option1_optimisation.get_optimised_route(orderid_list, address_list, API_Key_Tomtom,
                                                                        API_Key_Mapbox, start_datetime)
        optimisation_results = json.loads(optimisation_results)
        print(optimisation_results)
        sys.stdout.flush()   # free memory
    else:
        # do not optimise, just route and call ETA function
        
        My_times=[]  # empty array to store eta's
        Two_lat_long = '' # empty string to concatenate "lat,long:lat,long" 
       
        for i in (range(len(address_list)-1)):
           
            lat_long1 = option2_onlyETA.string_of_addrress(address_list[i],API_Key_Mapbox) # latitude,longitude 
            lat_long2 = option2_onlyETA.string_of_addrress(address_list[i+1],API_Key_Mapbox) # latitude,longitude 
            Two_lat_long = lat_long1 + ":" + lat_long2  # "lat,long:lat,long" 
            
            trip_time = option2_onlyETA.single_trip_Time(Two_lat_long,API_Key_Tomtom) #time it takes from one location to another
            
            My_times.append(trip_time) 
        
        ETA = []
        ETA.append(start_datetime.strftime("%H:%M:%S")) # convert starting time to hours , minutes and Seconds
        for j in range(len(My_times)):
            start_datetime = start_datetime + My_times[j]
            eta=start_datetime.strftime("%H:%M:%S") # convert each eat  to hours , minutes and Seconds
            ETA.append(eta)  # append each ETA
        
        
        optimisation_results = option2_onlyETA.to_json(orderid_list,address_list,ETA) # create object of orderid,addresses and ETA
        optimisation_results = json.loads(optimisation_results)
        print(optimisation_results)  # return the results
        sys.stdout.flush() # free memory



optimise_or_onlyETA(order_id, addresses, optimise_selection, start_datetime)
