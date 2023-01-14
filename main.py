# Brandt Davis, Student ID: 010385686

import csv
from ChainingHashTable import ChainingHashTable
from datetime import datetime, timedelta

print("Determining delivery route...\n")

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
    count = 0
    for i in range(1, len(dfPackagesList) + 1):
        if packageHashTable.search(i)[11] != "Delivered":
            count += 1
    return count

# Set soonest package to deliver
def setSoonest(soonestDeadline, soonestPackage, package, latest, currentLocation, dependency=False):
    if latest != "EOD":
        latestTime = datetime.strptime(latest, "%H:%M:%S")
        # If latest delivery time is earlier than soonestDeadline
        if soonestDeadline == None or latestTime < soonestDeadline:
            soonestDeadline = latestTime
            soonestPackage = package
        elif latestTime == soonestDeadline:
            if getDistance(package[12], currentLocation) < getDistance(soonestPackage[12], currentLocation):
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

def getDistance(location, currentLocation):
    locationRow = dfLocationsList[location - 1]
    if locationRow[currentLocation + 1]:
        return float(locationRow[currentLocation + 1])

    locationRow = dfLocationsList[currentLocation - 1]
    return float(locationRow[location + 1])

# Get next package delivery location
def getNextLocation(currentLocation, miles, startMiles, truck):
    shortest = hash = soonestDeadline = soonestPackage = soonestDependencyDeadline = soonestDependencyPackage = None
    locations = []
    dependent = False

    time = datetime.strptime("08:00", "%H:%M")
    timeChangeStartMiles = timedelta(hours=startMiles/18)
    startTime = time + timeChangeStartMiles

    # Set locations of packages to be delivered and soonest packages to be delivered to meet deadlines/dependency constraints
    for i in range(1, len(dfPackagesList) + 1):
        package = packageHashTable.search(i)
        if type(package[10]) == int:
            dependent = True


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

            if type(package[10]) == int:
                locationDistance = getDistance(package[12], currentLocation)
                if locationDistance == 0:
                    return deliverPackage(package[12], package, miles, startMiles, locationDistance)

                soonestDependencyDeadline, soonestDependencyPackage = setSoonest(soonestDependencyDeadline, soonestDependencyPackage, package, latest, currentLocation, dependency=True)
            else:
                if not dependent:
                    locationDistance = getDistance(package[12], currentLocation)
                    if locationDistance == 0:
                        return deliverPackage(package[12], package, miles, startMiles, locationDistance)
                soonestDeadline, soonestPackage = setSoonest(soonestDeadline, soonestPackage, package, latest, currentLocation)
                
            locations.append(package[1])

    # If there is a package with a deadline/dependency constraint, deliver this package ASAP
    for package in [soonestDependencyPackage, soonestPackage]:
        if package:
            locationDistance = getDistance(package[12], currentLocation)
            return deliverPackage(package[12], package, miles, startMiles, locationDistance)
    
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
    return None, miles, None


totalMiles1 = totalMiles2 = 0

# While there are packages to be delivered, set the next delivery route
packagesNotDelivered = getPackagesNotDelivered()
truck1route = []
truck2route = []
while packagesNotDelivered:
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
    truck1 = truck2 = False
    closestLocation1 = closestLocation2 = 1
    startMiles1, startMiles2 = totalMiles1, totalMiles2

    routeHashTable = ChainingHashTable()
    for i in range(1, len(dfLocationsList) + 1):
        routeHashTable.insert([i, 0])

    # Set a max delivery route of 16 packages
    for _ in range(16):
        if packagesNotDelivered > 16:
            for route, closestLocation, startMiles, totalMiles, truck, packages in [(route1, closestLocation1, startMiles1, totalMiles1, 1, packages1), (route2, closestLocation2, startMiles2, totalMiles2, 2, packages2)]:
                closestLocationtmp, totalMiles, package = getNextLocation(closestLocation, totalMiles, startMiles, truck)
                if closestLocationtmp == None:
                    break
                route.append(closestLocationtmp)

                if truck == 1:
                    truck1 = True
                    packages1.append(package[0])
                    route1 = route
                    closestLocation1 = closestLocationtmp
                    totalMiles1 = totalMiles
                else:
                    truck2 = True
                    route2 = route
                    closestLocation2 = closestLocationtmp
                    totalMiles2 = totalMiles
        else:
            closestLocationtmp, totalMiles, package = getNextLocation(closestLocation2, totalMiles2, startMiles2, 2)
            if closestLocationtmp == None:
                break
            closestLocation2 = closestLocationtmp
            route2.append(closestLocation2)

            truck2 = True
            packages2.append(package[0])
            totalMiles2 = totalMiles

    # Add the distance to return the truck to the hub
    if truck1:
        totalMiles1 += float(dfLocationsList[closestLocation1 - 1][2])
        route1.append(1)
    if truck2:
        totalMiles2 += float(dfLocationsList[closestLocation2 - 1][2])
        route2.append(1)
    for r in route1:
        truck1route.append(dfLocationsList[r - 1][1])
    for r in route2:
        truck2route.append(dfLocationsList[r - 1][1])
    packagesNotDelivered = getPackagesNotDelivered()

print("Truck 1 package route:")
for r in truck1route:
    print(r)
print("Total route miles: " + str(round(totalMiles1,2)))
print("\nTruck 2 package route:")
for r in truck2route:
    print(r)
print("Total route miles: " + str(round(totalMiles2, 2)))
print("\nTotal Miles: " + str(round(totalMiles1 + totalMiles2, 2)))
print("\nGet package delivery status at a certain time")
timestamp = input("Input time (HH:MM): ")

# Input validation on user specified time
while True:
    try:
        timestmp = datetime.strptime(timestamp, "%H:%M")
        break
    except:
        timestamp = input("Invalid time, Input time (HH:MM): ")
        continue

print("\n")
# Iterate over all packages and print the delivery status of each package at the user specified time
totalAtHub = 0
totalDelivered = 0
totalInRoute = 0
for i, row in enumerate(dfPackagesList, 1):
    package = packageHashTable.search(i)

    timestmp = datetime.strptime(timestamp, "%H:%M")

    deliveredTime = package[13]
    routeStartTime = package[14]

    deliveryStatus = "At Hub"
    if deliveredTime < timestmp:
        deliveryStatus = "Delivered At\t" + str(deliveredTime.time())
        totalDelivered += 1
    elif routeStartTime < timestmp:
        deliveryStatus = "In Route Since\t" + str(routeStartTime.time())
        totalInRoute += 1
    else:
        totalAtHub += 1
    print("Package ID: " + str(package[0]) + "\tDelivery Status: " + deliveryStatus)

print("\nTotal packages at hub: " + str(totalAtHub))
print("Total packages delivered: " + str(totalDelivered))
print("Total packages in route: " + str(totalInRoute))