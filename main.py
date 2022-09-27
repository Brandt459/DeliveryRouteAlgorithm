# Brandt Davis, Student ID: 010385686

import csv
from ChainingHashTable import ChainingHashTable
from datetime import datetime, timedelta

# Initiate package and location hash tables
packageHashTable = ChainingHashTable()
dfPackagesFile = open("package_file.csv", "r")
dfPackages = csv.reader(dfPackagesFile)
dfPackagesList = list(dfPackages)[1:]

locationHashTable = ChainingHashTable()
dfLocationsFile = open("distance_table.csv", "r")
dfLocations = csv.reader(dfLocationsFile)
dfLocationsList = list(dfLocations)[1:]

# Populate packageHashTable with package data from the package csv file
for i, row in enumerate(dfPackagesList, 1):
    package = []

    for a in range(11):
        if row[a].isdigit():
            package.append(int(row[a]))
        elif row[a].replace('.', '', 1).isdigit():
            package.append(float(row[a]))
        else:
            package.append(row[a])

    package.append("At the hub")
    for j, row1 in enumerate(dfLocationsList, 1):
        # If addresses are the same
        if row[1] in row1[1]:
            package.append(j)

    packageHashTable.insert(package)

# Populate locationHashTable with location data from the distance table csv file
for i, row in enumerate(dfLocationsList, 1):
    locationHashTable.insert([i, row[1]])

# Return True if there are packages to be delivered
def getPackagesNotDelivered():
    global dfPackages
    for i in range(1, len(dfPackagesList) + 1):
        if packageHashTable.search(i)[11] != "Delivered":
            return True
    return False

# Set soonest package to deliver
def setSoonest(soonestDeadline, soonestPackage, package, latest, dependency=False):
    if latest != "EOD":
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
def deliverPackage(location, package, miles, startMiles, currentLocationDistance):
    global dfLocations
    package[11] = "Delivered"
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
    return location, miles, package

# Get next package delivery location
def getNextLocation(currentLocation, miles, startMiles, truck):
    global dfPackages, dfLocations
    shortest = hash = soonestDeadline = soonestPackage = soonestDependencyDeadline = soonestDependencyPackage = None
    locations = []

    time = datetime.strptime("08:00", "%H:%M")
    timeChangeStartMiles = timedelta(hours=startMiles/18)
    startTime = time + timeChangeStartMiles

    # Set locations of packages to be delivered and soonest packages to be delivered to meet deadlines/dependency constraints
    for i in range(1, len(dfPackagesList) + 1):
        package = packageHashTable.search(i)
        if package[11] != "Delivered" and (type(package[8]) == str or package[8] == truck):
            earliest = package[7]
            latest = package[5]

            if earliest:
                earliestTime = datetime.strptime(earliest, "%H:%M:%S")
                # If earliest delivery time is after the route start time
                if earliestTime > startTime:
                    continue

            if type(package[10]) != str:
                soonestDependencyDeadline, soonestDependencyPackage = setSoonest(soonestDependencyDeadline, soonestDependencyPackage, package, latest, dependency=True)
            else:
                soonestDeadline, soonestPackage = setSoonest(soonestDeadline, soonestPackage, package, latest)
                
            locations.append(package[1])

    # If there is a package with a deadline/dependency constraint, deliver this package ASAP
    for package in [soonestDependencyPackage, soonestPackage]:
        if package:
            location = dfLocationsList[package[12] - 1]
            if location[currentLocation + 1]:
                return deliverPackage(package[12], package, miles, startMiles, float(location[currentLocation + 1]))

            location = dfLocationsList[currentLocation - 1]
            return deliverPackage(package[12], package, miles, startMiles, float(location[package[12] + 1]))

    # Find shortest distance to the next location with a package to be delivered
    for i, row in enumerate(dfLocationsList, 1):
        locationHash = locationHashTable.search(i)
        # If there is a package to be delivered to this location
        if locationHash[1] in locations:
            # If there is a value for the distance AND
            # (If there is no value in shortest OR
            # If the distance between the location and the current location is the shortest found so far)
            if row[currentLocation + 1] and (shortest == None or float(row[currentLocation + 1]) < shortest):
                shortest = float(row[currentLocation + 1])
                hash = locationHash
            elif dfLocationsList[currentLocation - 1][i + 1] and (shortest == None or float(dfLocationsList[currentLocation - 1][i + 1]) < shortest):
                shortest = float(dfLocationsList[currentLocation - 1][i + 1])
                hash = locationHash
            if locationHash[0] == currentLocation:
                shortest = 0
                hash = locationHash
                break

    # If shortest has a value, deliver a package to this location
    if shortest != None:
        for i in range(1, len(dfPackagesList) + 1):
            package = packageHashTable.search(i)
            if package[1] == hash[1] and package[11] != "Delivered":
                return deliverPackage(package[12], package, miles, startMiles, shortest)

    # If there are no locations to deliver a package to, return None
    return None, miles


totalMiles1 = totalMiles2 = 0

# While there are packages to be delivered, set the next delivery route
while getPackagesNotDelivered():
    '''
        If there is a package that has not been delivered:
            Run greedy algorithm 16 times to find which packages to load onto each truck first
            Return trucks to hub
            Continue until all packages have been delivered
    '''
    global startMiles1, startMiles2
    route1 = []
    route2 = []
    packages1 = []
    packages2 = []
    closestLocation1 = closestLocation2 = 1
    startMiles1, startMiles2 = totalMiles1, totalMiles2

    routeHashTable = ChainingHashTable()
    for i in range(1, len(dfLocationsList) + 1):
        routeHashTable.insert([i, 0])

    # Set a max delivery route of 16 packages
    for _ in range(16):
        for route, closestLocation, startMiles, totalMiles, truck in [(route1, closestLocation1, startMiles1, totalMiles1, 1), (route2, closestLocation2, startMiles2, totalMiles2, 2)]:
            closestLocationtmp, totalMiles, package = getNextLocation(closestLocation, totalMiles, startMiles, truck)
            if closestLocationtmp == None:
                break
            packages1.append(package)
            closestLocation = closestLocationtmp
            route.append(closestLocation)


            """ routeHash = routeHashTable.search(closestLocation1)
            routeHashTable.remove(closestLocation1)
            routeHash[1] += 1
            if routeHash[1] > 1:
                # If the index is not the index after the last encountered instance of location index,
                # Swap locations at the current index and index after the last encountered instance of location
                # Decrease route miles by the distance between the location before the current location, location after, and increase by the distance between the before and after location
                # Change package timestamps
                if len(route) - 1 != routeHash[-1] + 1:
                    tmp = route[routeHash[-1] + 1]
                    route[routeHash[-1] + 1] = closestLocation1
                    route[i] = tmp

                    prevLocation = route[i - 1]
                    currLocation = route[i]
                    nextLocation = route[i + 1]

                    # Subtract distance between previous location and current location
                    if dfLocationsList[prevLocation - 1][currLocation + 1]:
                        totalMiles -= float(dfLocationsList[prevLocation - 1][currLocation + 1])
                    else:
                        totalMiles -= float(dfLocationsList[currLocation - 1][prevLocation + 1])
                    
                    # Subtract distance between current location and next location
                    if dfLocationsList[currLocation - 1][nextLocation + 1]:
                        totalMiles -= float(dfLocationsList[currLocation - 1][nextLocation + 1])
                    else:
                        totalMiles -= float(dfLocationsList[nextLocation - 1][currLocation + 1])

                    # Add distance between previous location and next location
                    if dfLocationsList[prevLocation - 1][nextLocation + 1]:
                        totalMiles += float(dfLocationsList[prevLocation - 1][nextLocation + 1])
                    else:
                        totalMiles += float(dfLocationsList[nextLocation - 1][prevLocation + 1])
                    
                    routeHash.append(routeHash[-1] + 1)
                    
                    time = datetime.strptime("08:00", "%H:%M")
                    timeChange = timedelta(hours=miles/18)
                    timeChangeStartMiles = timedelta(hours=startMiles/18)
                    startTime = time + timeChangeStartMiles
                    time += timeChange

                    packages[i][12] = time
                    packages[i][13] = startTime
                else:
                    routeHash.append(i)
            else:
                    routeHash.append(i)
            routeHashTable.insert(routeHash) """


    """ # Reorganizing route to save miles by delivering to the same location without having to backtrack.
    # This will only allow the truck to reach future locations faster, so delivery deadlines won't be effected.
    # Package dependencies also will not be effected since the same packages are still on the truck, the order is just reorganized.
    for index, route in enumerate([route1, route2]):
        totalMiles = totalMiles1
        packages = packages1
        if index == 1:
            totalMiles = totalMiles2
            packages = packages2
        routeHashTable = ChainingHashTable()
        for i in range(1, len(dfLocationsList) + 1):
            routeHashTable.insert([i, 0])
        # Increment route location count by 1
        for i, location in enumerate(route):
            routeHash = routeHashTable.search(location)
            routeHashTable.remove(location)
            routeHash[1] += 1
            if routeHash[1] > 1:
                # If the index is not the index after the last encountered instance of location index,
                # Swap locations at the current index and index after the last encountered instance of location
                # Decrease route miles by the distance between the location before the current location, location after, and increase by the distance between the before and after location
                # Change package timestamps
                if i != routeHash[-1] + 1:
                    tmp = route[routeHash[-1] + 1]
                    route[routeHash[-1] + 1] = location
                    route[i] = tmp

                    prevLocation = route[i - 1]
                    currLocation = route[i]
                    nextLocation = route[i + 1]

                    # Subtract distance between previous location and current location
                    if dfLocationsList[prevLocation - 1][currLocation + 1]:
                        totalMiles -= float(dfLocationsList[prevLocation - 1][currLocation + 1])
                    else:
                        totalMiles -= float(dfLocationsList[currLocation - 1][prevLocation + 1])
                    
                    # Subtract distance between current location and next location
                    if dfLocationsList[currLocation - 1][nextLocation + 1]:
                        totalMiles -= float(dfLocationsList[currLocation - 1][nextLocation + 1])
                    else:
                        totalMiles -= float(dfLocationsList[nextLocation - 1][currLocation + 1])

                    # Add distance between previous location and next location
                    if dfLocationsList[prevLocation - 1][nextLocation + 1]:
                        totalMiles += float(dfLocationsList[prevLocation - 1][nextLocation + 1])
                    else:
                        totalMiles += float(dfLocationsList[nextLocation - 1][prevLocation + 1])
                    
                    routeHash.append(routeHash[-1] + 1)
                    
                    time = datetime.strptime("08:00", "%H:%M")
                    timeChange = timedelta(hours=miles/18)
                    timeChangeStartMiles = timedelta(hours=startMiles/18)
                    startTime = time + timeChangeStartMiles
                    time += timeChange

                    packages[i][12] = time
                    packages[i][13] = startTime
                else:
                    routeHash.append(i)
            else:
                    routeHash.append(i)
            routeHashTable.insert(routeHash)
        if index == 0:
            totalMiles1 = totalMiles
        else:
            totalMiles2 = totalMiles """

    # Add the distance to return the truck to the hub
    totalMiles1 += float(dfLocationsList[closestLocation1 - 1][2])
    totalMiles2 += float(dfLocationsList[closestLocation2 - 1][2])

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
for i, row in enumerate(dfPackagesList, 1):
    package = packageHashTable.search(i)

    timestmp = datetime.strptime(timestamp, "%H:%M")

    deliveredTime = package[13]
    routeStartTime = package[14]

    deliveryStatus = "At Hub"
    if deliveredTime < timestmp:
        deliveryStatus = "Delivered At " + str(deliveredTime.time())
    elif routeStartTime < timestmp:
        deliveryStatus = "In Route Since " + str(routeStartTime.time())
    print("Package ID: " + str(package[0]) + " Delivery Status: " + deliveryStatus)
