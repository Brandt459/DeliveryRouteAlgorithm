import csv
from ChainingHashTable import ChainingHashTable
from datetime import datetime, timedelta

print("Determining delivery route...\n")

# Initiate package and location hash tables
packageHashTable = ChainingHashTable()
dfPackagesFile = open("package_file.csv", "r")
dfPackages = csv.reader(dfPackagesFile)
dfPackagesList = list(dfPackages)

locationHashTable = ChainingHashTable()
dfLocationsFile = open("distance_table.csv", "r")
dfLocations = csv.reader(dfLocationsFile)
dfLocationsList = list(dfLocations)

# Populate packageHashTable with package data from the package csv file
packageKeys = dfPackagesList[0]
for row in dfPackagesList[1:]:
    package = {}

    for a in range(len(packageKeys)):
        if row[a].isdigit():
            package[packageKeys[a]] = int(row[a])
        else:
            package[packageKeys[a]] = row[a]

    package['status'] = "At the hub"
    for i, locationRow in enumerate(dfLocationsList[1:], 1):
        # If addresses are the same
        if row[1] in locationRow[1]:
            package['locationId'] = i

    packageHashTable.insert(package)

# Populate locationHashTable with location data from the distance table csv file
locationKeys = dfLocationsList[0]
for i, row in enumerate(dfLocationsList[1:], 1):
    locationHashTable.insert({'locationId': i, 'address': row[1]})

# Return True if there are packages to be delivered
def getPackagesNotDelivered():
    count = 0
    for i in range(1, len(dfPackagesList)):
        if packageHashTable.search(i)['status'] != "Delivered":
            count += 1
    return count

# Set soonest package to deliver
def setSoonest(soonestDeadline, soonestPackage, package, currentLocation, dependency=False):
    if package['deliveryDeadline'] != "EOD":
        latestTime = datetime.strptime(package['deliveryDeadline'], "%H:%M:%S")
        # If latest delivery time is earlier than soonestDeadline
        if soonestDeadline == None or latestTime < soonestDeadline:
            soonestDeadline = latestTime
            soonestPackage = package
        elif latestTime == soonestDeadline:
            if getDistance(package['locationId'], currentLocation) < getDistance(soonestPackage['locationId'], currentLocation):
                soonestDeadline = latestTime
                soonestPackage = package
    if dependency:
        if soonestDeadline == None:
            soonestPackage = package
    return soonestDeadline, soonestPackage

# Set package delivery status to Delivered and set delivery timestamps
def deliverPackage(package, miles, startMiles, currentLocationDistance):
    package['status'] = "Delivered"
    miles += currentLocationDistance
    time = datetime.strptime("08:00", "%H:%M")
    timeChange = timedelta(hours=miles/18)
    timeChangeStartMiles = timedelta(hours=startMiles/18)
    startTime = time + timeChangeStartMiles
    time += timeChange
    package['deliveredTime'] = time
    package['routeStartTime'] = startTime
    packageHashTable.remove(package['packageId'])
    packageHashTable.insert(package)
    return miles, package

def getDistance(location, currentLocation):
    locationRow = dfLocationsList[location]
    if locationRow[currentLocation + 1]:
        return float(locationRow[currentLocation + 1])

    locationRow = dfLocationsList[currentLocation]
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
    for i in range(1, len(dfPackagesList)):
        package = packageHashTable.search(i)
        if type(package['dependency1']) == int:
            dependent = True


    for i in range(1, len(dfPackagesList)):
        package = packageHashTable.search(i)
        if package['status'] != "Delivered" and (type(package['truck']) == str or package['truck'] == truck):
            earliest = package['earliest']

            if earliest:
                earliestTime = datetime.strptime(earliest, "%H:%M:%S")
                # If earliest delivery time is after the route start time
                if earliestTime > startTime:
                    continue

            if type(package['dependency2']) == int:
                locationDistance = getDistance(package['locationId'], currentLocation)
                if locationDistance == 0:
                    return deliverPackage(package, miles, startMiles, locationDistance)

                soonestDependencyDeadline, soonestDependencyPackage = setSoonest(soonestDependencyDeadline, soonestDependencyPackage, package, currentLocation, dependency=True)
            else:
                if not dependent:
                    locationDistance = getDistance(package['locationId'], currentLocation)
                    if locationDistance == 0:
                        return deliverPackage(package, miles, startMiles, locationDistance)
                soonestDeadline, soonestPackage = setSoonest(soonestDeadline, soonestPackage, package, currentLocation)
                
            locations.append(package['address'])

    # If there is a package with a deadline/dependency constraint, deliver this package ASAP
    for package in [soonestDependencyPackage, soonestPackage]:
        if package:
            locationDistance = getDistance(package['locationId'], currentLocation)
            return deliverPackage(package, miles, startMiles, locationDistance)
    
    # Find shortest distance to the next location with a package to be delivered
    for i, row in enumerate(dfLocationsList[1:], 1):
        locationHash = locationHashTable.search(i)
        # If there is a package to be delivered to this location
        if locationHash['address'] in locations:
            # If there is a value for the distance AND
            # (If there is no value in shortest OR
            # If the distance between the location and the current location is the shortest found so far)
            if row[currentLocation + 1] and (shortest == None or float(row[currentLocation + 1]) < shortest):
                shortest = float(row[currentLocation + 1])
                hash = locationHash
            elif dfLocationsList[currentLocation][i + 1] and (shortest == None or float(dfLocationsList[currentLocation][i + 1]) < shortest):
                shortest = float(dfLocationsList[currentLocation][i + 1])
                hash = locationHash
            if locationHash['locationId'] == currentLocation:
                shortest = 0
                hash = locationHash
                break

    # If shortest has a value, deliver a package to this location
    if shortest != None:
        for i in range(1, len(dfPackagesList)):
            package = packageHashTable.search(i)
            if package['address'] == hash['address'] and package['status'] != "Delivered":
                return deliverPackage(package, miles, startMiles, shortest)

    # If there are no locations to deliver a package to, return None
    return miles, None


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

    # Set a max delivery route of 16 packages
    for _ in range(16):
        if packagesNotDelivered > 16:
            for route, closestLocation, startMiles, totalMiles, truck, packages in [(route1, closestLocation1, startMiles1, totalMiles1, 1, packages1), (route2, closestLocation2, startMiles2, totalMiles2, 2, packages2)]:
                totalMiles, package = getNextLocation(closestLocation, totalMiles, startMiles, truck)
                if not package: break
                closestLocationtmp = package['locationId']
                route.append(closestLocationtmp)

                if truck == 1:
                    truck1 = True
                    packages1.append(package['packageId'])
                    route1 = route
                    closestLocation1 = closestLocationtmp
                    totalMiles1 = totalMiles
                else:
                    truck2 = True
                    route2 = route
                    closestLocation2 = closestLocationtmp
                    totalMiles2 = totalMiles
        else:
            totalMiles, package = getNextLocation(closestLocation2, totalMiles2, startMiles2, 2)
            if not package: break
            closestLocationtmp = package['locationId']
            closestLocation2 = closestLocationtmp
            route2.append(closestLocation2)

            truck2 = True
            packages2.append(package['packageId'])
            totalMiles2 = totalMiles

    # Add the distance to return the truck to the hub
    if truck1:
        totalMiles1 += float(dfLocationsList[closestLocation1][2])
        route1.append(1)
    if truck2:
        totalMiles2 += float(dfLocationsList[closestLocation2][2])
        route2.append(1)
    for r in route1:
        truck1route.append(dfLocationsList[r][1])
    for r in route2:
        truck2route.append(dfLocationsList[r][1])
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
for i in range(1, len(dfPackagesList)):
    package = packageHashTable.search(i)

    timestmp = datetime.strptime(timestamp, "%H:%M")

    deliveredTime = package['deliveredTime']
    routeStartTime = package['routeStartTime']

    deliveryStatus = "At Hub"
    if deliveredTime < timestmp:
        deliveryStatus = "Delivered At\t" + str(deliveredTime.time())
        totalDelivered += 1
    elif routeStartTime < timestmp:
        deliveryStatus = "In Route Since\t" + str(routeStartTime.time())
        totalInRoute += 1
    else:
        totalAtHub += 1
    print("Package ID: " + str(package['packageId']) + "\tDelivery Status: " + deliveryStatus)

print("\nTotal packages at hub: " + str(totalAtHub))
print("Total packages delivered: " + str(totalDelivered))
print("Total packages in route: " + str(totalInRoute))