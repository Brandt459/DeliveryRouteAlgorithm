# Brandt Davis, Student ID: 010385686

from ChainingHashTable import ChainingHashTable
import pandas as pd
from datetime import datetime
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


def getNextLocation(currentLocation, miles, time):
    shortest = None
    closestLocation = None
    hash = None
    addr = None
    currentLocationIndex = None
    for i in range(1, len(dfLocations) + 1):
        location = dfLocations.loc[i - 1]
        locationHash = locationHashTable.search(i)
        # Location is not the same as the current location AND
        # Atleast 1 package needs to be delivered to the location
        if location["Location"] != currentLocation and locationHash[3] > 0:
            # If there is no value in shortest OR
            # If the distance between the location and the current location is the shortest found so far
            if not np.isnan(location[currentLocation]) and (shortest == None or location[currentLocation] < shortest):
                shortest = location[currentLocation]
                closestLocation = location["Location"]
                hash = locationHash
                addr = location["Location1"]
        else:
            currentLocationIndex = i - 1

    # Second iteration, iterate over currentLocation distances
    for i in range(30):
        location = dfLocations.loc[currentLocationIndex]
        for index, (name, value) in enumerate(location.iteritems()):
            if index > 1:
                locationHash = locationHashTable.search(index - 1)
                if name != currentLocation and locationHash[3] > 0:
                    # If there is no value in shortest OR
                    # If the distance between the location and the current location is the shortest found so far
                    if not np.isnan(value) and (shortest == None or value < shortest):
                        shortest = value
                        closestLocation = name
                        hash = locationHash
                        addr = locationHash[2]

    if shortest:
        miles += shortest
        # Decrement packages to deliver to the location by one
        locationHashTable.remove(hash[0])
        hash[3] -= 1
        locationHashTable.insert(hash)
        for i in range(1, len(dfPackages) + 1):
            package = packageHashTable.search(i)
            if package[1] == addr and package[8] != "Delivered":
                earliest = package[6]
                latest = package[2]

                """ if not np.isnan(earliest):
                    earliestTime = datetime.strptime(earliest, "%H:%M:%S")
                    # If earliest delivery time is after the current time
                    if earliestTime > time:
                        pass

                if not np.isnan(latest):
                    latestTime = datetime.strptime(latest, "%H:%M:%S")
                    # If latest delivery time is before the current time
                    if latestTime < time:
                        pass """

                package[8] = "Delivered"
                packageHashTable.remove(package[0])
                packageHashTable.insert(package)
                break
    return closestLocation, miles


totalMiles = 0
time = datetime.strptime("08:00", "%H:%M")

while getPackagesNotDelivered():
    '''
        If there is a package that has not been delivered:
            Run greedy algorithm 16 times to find which packages to load onto the truck first
            Return to hub
            Continue until all packages have been delivered
    '''
    route = []
    closestLocation = locationHashTable.search(1)[1]
    mileage = 0
    for _ in range(16):
        closestLocation, miles = getNextLocation(closestLocation, mileage, time)
        mileage = miles
        if closestLocation == None:
            break
        route.append(closestLocation)

    for i in range(1, len(dfLocations) + 1):
        location = dfLocations.loc[i - 1]
        if location["Location"] == closestLocation:
            mileage += location[locationHashTable.search(1)[1]]
    totalMiles += mileage

print(totalMiles)


# Part 1: How many packages per location

""" for i in range(1, len(dfPackages) + 1):
    package = packageHashTable.search(i)
    location = locationHashTable.search(package[9])
    locationHashTable.remove(package[9])
    location[3] += 1
    locationHashTable.insert(location)
    for j in range(1, len(dfPackages) + 1):
        # If addresses are equal
        package2 = packageHashTable.search(j)
        if package[1] == package2[1]:
            earliest1 = datetime.strptime("08:00", "%H:%M")
            earliest2 = datetime.strptime("08:00", "%H:%M")
            latest1 = datetime.strptime("23:59", "%H:%M")
            latest2 = datetime.strptime("23:59", "%H:%M")
            if type(package[6]) == str:
                earliest1 = datetime.strptime(str(package[6]), "%H:%M:%S")
            if type(package2[6]) == str:
                earliest2 = datetime.strptime(str(package2[6]), "%H:%M:%S")
            if type(package[2]) == str and package[2] != "EOD":
                latest1 = datetime.strptime(str(package[2]), "%H:%M:%S")
            if type(package2[2]) == str  and package2[2] != "EOD":
                latest2 = datetime.strptime(str(package2[2]), "%H:%M:%S")
            # If delivery windows overlap
            if earliest1 < latest2 and earliest2 < latest1: """



# Part 2: Same time deliveries

