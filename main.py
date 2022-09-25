# Brandt Davis, Student ID: 010385686

from ChainingHashTable import ChainingHashTable
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

# Initiate package and location hash tables
packageHashTable = ChainingHashTable()
dfPackages = pd.read_csv("package_file.csv")

locationHashTable = ChainingHashTable()
dfLocations = pd.read_csv("distance_table.csv")

# Populate packageHashTable with package data from the package csv file
for i in range(len(dfPackages)):
    package = []
    cols = ["Package ID", "Address", "Delivery Deadline", "City", "Zip", "KILOs", "Earliest", "Truck", "Dependency1", "Dependency2"]

    for col in cols:
        package.append(dfPackages.loc[i][col])

    package.append("At the hub")
    for j in range(len(dfLocations)):
        if dfPackages.loc[i]["Address"] in dfLocations.loc[j]["Location1"]:
            package.append(j + 1)

    packageHashTable.insert(package)

# Populate locationHashTable with location data from the distance table csv file
for i in range(len(dfLocations)):
    location = dfLocations.loc[i]["Location"]
    location1 = dfLocations.loc[i]["Location1"]
    locationHashTable.insert([i + 1, location, location1])

# Return True if there are packages to be delivered
def getPackagesNotDelivered():
    for i in range(1, len(dfPackages) + 1):
        if packageHashTable.search(i)[10] != "Delivered":
            return True
    return False

# Set soonest package to deliver
def setSoonest(soonestDeadline, soonestPackage, package, latest, dependency=False):
    if type(latest) == str and latest != "EOD":
        latestTime = datetime.strptime(latest, "%H:%M:%S")
        # If latest delivery time is earlier than soonestDeadline
        if soonestDeadline == None or latestTime < soonestDeadline:
            soonestDeadline = latestTime
            soonestPackage = package
    if dependency:
        if soonestDeadline == None:
            soonestPackage = package
    return soonestDeadline, soonestPackage

# Set package delivery status to Delivered and set delivery timestamps
def deliverPackage(locationHash, package, miles, startMiles, currentLocationDistance):
    package[10] = "Delivered"
    miles += currentLocationDistance
    time = datetime.strptime("08:00", "%H:%M")
    timeChange = timedelta(hours=miles/18)
    timeChangeStartMiles = timedelta(hours=startMiles/18)
    startTime = time + timeChangeStartMiles
    time += timeChange
    package.append(time)
    package.append(startTime)
    packageHashTable.remove(package[0])
    packageHashTable.insert(package)
    return locationHash[2], miles

# Get next package delivery location
def getNextLocation(currentLocation, miles, startMiles, truck):
    shortest = None
    hash = None
    locations = []
    currentLocationIndex = None

    soonestDeadline = None
    soonestPackage = None

    soonestDependencyDeadline = None
    soonestDependencyPackage = None

    time = datetime.strptime("08:00", "%H:%M")
    timeChange = timedelta(hours=miles/18)
    timeChangeStartMiles = timedelta(hours=startMiles/18)
    startTime = time + timeChangeStartMiles
    time += timeChange

    # Set locations of packages to be delivered and soonest packages to be delivered to meet deadlines/dependency constraints
    for i in range(1, len(dfPackages) + 1):
        package = packageHashTable.search(i)
        if package[10] != "Delivered" and (np.isnan(package[7]) or package[7] == truck):
            earliest = package[6]
            latest = package[2]

            if type(earliest) == str:
                earliestTime = datetime.strptime(earliest, "%H:%M:%S")
                # If earliest delivery time is after the route start time
                if earliestTime > startTime:
                    continue

            if not np.isnan(package[9]):
                soonestDependencyDeadline, soonestDependencyPackage = setSoonest(soonestDependencyDeadline, soonestDependencyPackage, package, latest, dependency=True)
            else:
                soonestDeadline, soonestPackage = setSoonest(soonestDeadline, soonestPackage, package, latest)
                
            locations.append(package[1])

    # If there is a package with a deadline/dependency constraint, deliver this package ASAP
    for var in [soonestDependencyPackage, soonestPackage]:
        if var:
            location = dfLocations.loc[var[11] - 1]
            locationHash = locationHashTable.search(var[11])

            if not np.isnan(location[currentLocation]):
                return deliverPackage(locationHash, var, miles, startMiles, location[currentLocation])

            for i in range(1, len(dfLocations) + 1):
                locationHash = locationHashTable.search(i)
                if locationHash[2] == currentLocation:
                    location = dfLocations.loc[i - 1]
                    for index, (name, value) in enumerate(location.iteritems()):
                        if index > 1:
                            locationHash = locationHashTable.search(index - 1)
                            if locationHash[2] == var[1]:
                                if not np.isnan(value):
                                    return deliverPackage(locationHash, var, miles, startMiles, location[currentLocation])
                    break

    # Find shortest distance to the next location with a package to be delivered
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
    if shortest != 0:
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

    # If shortest has a value, deliver a package to this location
    if shortest != None:
        for i in range(1, len(dfPackages) + 1):
            package = packageHashTable.search(i)
            if package[1] == hash[2] and package[10] != "Delivered":
                return deliverPackage(hash, package, miles, startMiles, shortest)
                break
    
    # If there are no locations to deliver a package to, return None
    return None, miles


totalMiles1 = 0
totalMiles2 = 0

# While there are packages to be delivered, set the next delivery route
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

    # Set a max delivery route of 16 packages
    for _ in range(16):
        closestLocation1, totalMiles1 = getNextLocation(closestLocation1, totalMiles1, startMiles1, 1)
        closestLocation2, totalMiles2 = getNextLocation(closestLocation2, totalMiles2, startMiles2, 2)
        if closestLocation1 == None:
            break
        if closestLocation2 == None:
            break
        route1.append(closestLocation1)
        route2.append(closestLocation2)

    # Add the distance to return the truck to the hub
    for i in range(1, len(dfLocations) + 1):
        location = dfLocations.loc[i - 1]
        if location["Location"] == closestLocation1:
            totalMiles1 += location[locationHashTable.search(1)[1]]
        if location["Location"] == closestLocation2:
            totalMiles2 += location[locationHashTable.search(1)[1]]

print("Total Miles: " + str(totalMiles1 + totalMiles2))
timestamp = input("Input time (HH:MM): ")

# Input validation on user specified time
while True:
    try:
        timestmp = datetime.strptime(timestamp, "%H:%M")
        break
    except:
        timestamp = input("Invalid time, Input time (HH:MM): ")
        continue

# Iterate over all packages and print the delivery status of each package at the user specified time
for i in range(1, len(dfPackages) + 1):
    package = packageHashTable.search(i)

    timestmp = datetime.strptime(timestamp, "%H:%M")

    deliveredTime = package[12]
    routeStartTime = package[13]

    deliveryStatus = "At Hub"
    if deliveredTime < timestmp:
        deliveryStatus = "Delivered At " + str(deliveredTime.time())
    elif routeStartTime < timestmp:
        deliveryStatus = "In Route Since " + str(routeStartTime.time())
    print("Package ID: " + str(package[0]) + " Delivery Status: " + deliveryStatus)
