# Brandt Davis, Student ID: 010385686

from ChainingHashTable import ChainingHashTable
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Initiate and populate package and location hash tables
packageHashTable = ChainingHashTable()
dfPackages = pd.read_csv("package_file.csv")

locationHashTable = ChainingHashTable()
dfLocations = pd.read_csv("distance_table.csv")


for i in range(len(dfPackages)):
    package = []
    cols = ["Package ID", "Address", "Delivery Deadline", "City", "Zip", "KILOs", "Earliest", "Truck"]

    for col in cols:
        package.append(dfPackages.loc[i][col])

    package.append("At the hub")
    for j in range(len(dfLocations)):
        if dfPackages.loc[i]["Address"] in dfLocations.loc[j]["Location1"]:
            package.append(j + 1)

    packageHashTable.insert(package)

for i in range(len(dfLocations)):
    location = dfLocations.loc[i]["Location"]
    location1 = dfLocations.loc[i]["Location1"]
    locationHashTable.insert([i + 1, location, location1, 0])

for i in range(1, len(dfPackages) + 1):
    package = packageHashTable.search(i)
    location = locationHashTable.search(package[9])
    locationHashTable.remove(package[9])
    location[3] += 1
    locationHashTable.insert(location)


def getPackagesNotDelivered():
    count = 0
    for i in range(1, len(dfPackages) + 1):
        if packageHashTable.search(i)[8] != "Delivered":
            count += 1
    if count > 0:
        return True
    return False


def getNextLocation(currentLocation, miles, startMiles, truck):
    shortest = None
    hash = None
    locations = []
    currentLocationIndex = None

    soonestDeadline = None
    soonestPackage = None

    time = datetime.strptime("08:00", "%H:%M")
    timeChange = timedelta(hours=miles/18)
    timeChangeStartMiles = timedelta(hours=startMiles/18)
    startTime = time + timeChangeStartMiles
    time = time + timeChange
    for i in range(1, len(dfPackages) + 1):
        package = packageHashTable.search(i)
        if package[8] != "Delivered" and (np.isnan(package[7]) or package[7] == truck):
            earliest = package[6]
            latest = package[2]
            
            if type(latest) == str and latest != "EOD":
                latestTime = datetime.strptime(latest, "%H:%M:%S")
                # If latest delivery time is earlier than soonestDeadline
                if soonestDeadline == None or latestTime < soonestDeadline:
                    soonestDeadline = latestTime
                    soonestPackage = package

            if type(earliest) == str:
                earliestTime = datetime.strptime(earliest, "%H:%M:%S")
                # If earliest delivery time is after the route start time
                if earliestTime > startTime:
                    continue

            locations.append(package[1])

    if soonestDeadline:
        location = dfLocations.loc[soonestPackage[9] - 1]
        locationHash = locationHashTable.search(soonestPackage[9])

        if not np.isnan(location[currentLocation]):
            hash = locationHash
            locationHashTable.remove(hash[0])
            hash[3] -= 1
            locationHashTable.insert(hash)
            soonestPackage[8] = "Delivered"
            packageHashTable.remove(soonestPackage[0])
            packageHashTable.insert(soonestPackage)
            miles += location[currentLocation]
            return locationHash[2], miles

        for i in range(1, len(dfLocations) + 1):
            locationHash = locationHashTable.search(i)
            if locationHash[2] == currentLocation:
                location = dfLocations.loc[i - 1]
                for index, (name, value) in enumerate(location.iteritems()):
                    if index > 1:
                        locationHash = locationHashTable.search(index - 1)
                        if locationHash[2] == soonestPackage[1]:
                            if not np.isnan(value):
                                hash = locationHash
                                locationHashTable.remove(hash[0])
                                hash[3] -= 1
                                locationHashTable.insert(hash)
                                soonestPackage[8] = "Delivered"
                                packageHashTable.remove(soonestPackage[0])
                                packageHashTable.insert(soonestPackage)
                                miles += location[currentLocation]
                                return locationHash[2], miles
                break

    for i in range(1, len(dfLocations) + 1):
        location = dfLocations.loc[i - 1]
        locationHash = locationHashTable.search(i)
        # If there is a package to be delivered to this location
        if locationHash[2] in locations:
            # If there is a value for the distance AND
            # (If there is no value in shortest OR
            # If the distance between the location and the current location is the shortest found so far)
            if not np.isnan(location[currentLocation]) and (shortest == None or location[currentLocation] < shortest):
                shortest = location[currentLocation]
                hash = locationHash
            if locationHash[2] == currentLocation:
                shortest = 0
                hash = locationHash
                break
        if locationHash[2] == currentLocation:
            currentLocationIndex = i - 1

    # Second iteration, iterate over currentLocation distances
    if shortest == None or shortest > 0:
        location = dfLocations.loc[currentLocationIndex]
        for index, (name, value) in enumerate(location.iteritems()):
            if index > 1:
                locationHash = locationHashTable.search(index - 1)
                if locationHash[2] in locations:
                    # If there is no value in shortest OR
                    # If the distance between the location and the current location is the shortest found so far
                    if not np.isnan(value) and (shortest == None or value < shortest):
                        shortest = value
                        hash = locationHash

    if type(shortest) in [float, int, np.float64]:
        miles += shortest
        # Decrement packages to deliver to the location by one
        locationHashTable.remove(hash[0])
        hash[3] -= 1
        locationHashTable.insert(hash)
        for i in range(1, len(dfPackages) + 1):
            package = packageHashTable.search(i)
            if package[1] == hash[2] and package[8] != "Delivered":
                package[8] = "Delivered"
                packageHashTable.remove(package[0])
                packageHashTable.insert(package)
                break
    if not hash:
        return None, miles
    return hash[2], miles


totalMiles1 = 0
totalMiles2 = 0


while getPackagesNotDelivered():
    '''
        If there is a package that has not been delivered:
            Run greedy algorithm 16 times to find which packages to load onto each truck first
            Return trucks to hub
            Continue until all packages have been delivered
    '''
    route1 = []
    route2 = []
    closestLocation1 = locationHashTable.search(1)[2]
    closestLocation2 = locationHashTable.search(1)[2]
    startMiles1 = totalMiles1
    startMiles2 = totalMiles2
    for _ in range(16):
        closestLocation1, miles1 = getNextLocation(closestLocation1, totalMiles1, startMiles1, 1)
        totalMiles1 = miles1
        closestLocation2, miles2 = getNextLocation(closestLocation2, totalMiles2, startMiles2, 2)
        totalMiles2 = miles2
        if closestLocation1 == None:
            break
        if closestLocation2 == None:
            break
        route1.append(closestLocation1)
        route2.append(closestLocation2)

    for i in range(1, len(dfLocations) + 1):
        location = dfLocations.loc[i - 1]
        if location["Location"] == closestLocation1:
            totalMiles1 += location[locationHashTable.search(1)[1]]
        if location["Location"] == closestLocation2:
            totalMiles2 += location[locationHashTable.search(1)[1]]

print(totalMiles1 + totalMiles2)
