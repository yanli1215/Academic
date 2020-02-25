# Python Modules
import json
import tkinter
import tkinter.font
from tkinter import messagebox
from operator import itemgetter
import datetime

# Load Functions (Yanli & Tiffany)
def load_canteens():

	canteensFile = open("canteens.json", "r")

	canteensJSON = canteensFile.read()
	canteensDict = json.loads(canteensJSON)

	canteensFile.close()
	
	return canteensDict

def load_buses():

	busesFile = open("buses.json", "r")

	busesJSON = busesFile.read()
	busesDict = json.loads(busesJSON)

	busesFile.close()
	
	return busesDict

def load_food_info(database):
	# Create a list containining every food's canteen, stall, name & price
	foodInfo = []

	for i in database:
		for j in database[i]["stalls"]:
			for food_name in database[i]["stalls"][j]["food"]:
				foodInfo.append([i, j, food_name, database[i]["stalls"][j]["food"][food_name]["price"]])

	return foodInfo


# Canteen & bus information
canteensDict = load_canteens()
busesDict = load_buses()
foodInfo = load_food_info(canteensDict)


# Map GUI Functions (Tiffany)
MAP_WIDTH = 1422
MAP_HEIGHT = 850

def get_location():

	# Instruct the user on what to do
	messagebox.showinfo("How to Use", "Use the mouse to click on your current position")

	# Create a window
	mapRoot = tkinter.Toplevel()
	mapRoot.title("NTU Map")


	# Create a canvas
	canvas = tkinter.Canvas(mapRoot, width = MAP_WIDTH, height = MAP_HEIGHT)
	canvas.pack()


	# Display the map
	ntuMap = tkinter.PhotoImage(file = "ntuMap.png")
	canvas.create_image(0, 0, anchor = tkinter.NW, image = ntuMap)

	# Check for mouse clicks (store in location & close window if there's a click)
	location = None

	def onMouseClick(event):
		nonlocal location
		location = (event.x, event.y)
		mapRoot.destroy()

	canvas.bind("<Button-1>", onMouseClick)


	# Handle window closing (check if window closed manually or by mouse click)
	running = True

	def onWindowClose():
		nonlocal running
		running = False
		mapRoot.destroy()

	mapRoot.protocol("WM_DELETE_WINDOW", onWindowClose)


	# Keep the window open as long as it's not closed manually or by mouse click
	while running and location is None:
		mapRoot.update_idletasks()
		mapRoot.update()
	if location != None:
		display_locations(user_location = location)

	return location

def locations_of_canteens(database, list_of_canteens):

	# Return the list of locations of canteens in order
	locations = [database[canteen]["location"] for canteen in list_of_canteens]
	return locations

def display_locations(locations = None, user_location = None, numbered = False):

	# Create a window
	mapRoot = tkinter.Toplevel()
	mapRoot.title("NTU Map")


	# Create a canvas
	canvas = tkinter.Canvas(mapRoot, width = MAP_WIDTH, height = MAP_HEIGHT)
	canvas.pack()

	# Display the map
	ntuMap = tkinter.PhotoImage(file = "ntuMap.png")
	canvas.create_image(0, 0, anchor = tkinter.NW, image = ntuMap)

	# Create a marker
	marker = tkinter.PhotoImage(file = "marker.png")
	markerWidth = marker.width()
	markerHeight = marker.height()

	# Display the locations
	if locations != None:
		markers = [marker] * len(locations)

		for i in range(len(locations)):
			location = locations[i]
			
			# Add a number label
			if numbered:
				numberLabel = tkinter.Label(canvas, text = str(i + 1), fg = "white", bg = "black")
				numberLabel.place(x = location[0] + markerWidth / 2, y = location[1] - (markerHeight + 10 + 5))

			canvas.create_image(location[0] - markerWidth / 2, location[1] - markerHeight, anchor = tkinter.NW, image = markers[i])

	# Display your location
	if user_location != None:
		youLabel = tkinter.Label(canvas, text = "You", fg = "white", bg = "black")
		youLabel.place(x = user_location[0] + markerWidth / 2, y = user_location[1] - (markerHeight + 10 + 5))

		marker = tkinter.PhotoImage(file = "marker.png")
		canvas.create_image(user_location[0] - markerWidth / 2, user_location[1] - markerHeight, anchor = tkinter.NW, image = marker)

	# Handle window closing (check if window closed manually or by mouse click)
	running = True

	def onWindowClose():
		nonlocal running
		running = False
		mapRoot.destroy()

	mapRoot.protocol("WM_DELETE_WINDOW", onWindowClose)


	# Keep the window open as long as it's not closed manually or by mouse click
	while running:
		mapRoot.update_idletasks()
		mapRoot.update()


# Travel Time Functions (Yanli & Tiffany)
METRES_PER_PIXEL = 1.7 # m/px (about 860px to 1.46km)
AVERAGE_WALKING_SPEED = 84 # m/min
BUS_STOP_TIME = 1 # min
BUS_WAITING_TIME = 2 # min

def distance_a_b(location_of_a, location_of_b):

	# Using Pythagoras' Theorem
	distance = ((location_of_a[0] - location_of_b[0]) ** 2 + (location_of_a[1] - location_of_b[1]) ** 2) ** 0.5
	return distance

def get_nearest_bus_stops(busesDict, point):

	# Creates a dictionary of the nearest bus stops {bus: {name: nearestBusStop, distance: distanceToBusStop}}
	nearestBusStops = {}

	for bus in busesDict:
		busStops = busesDict[bus]["bus route"]


		# Initialise the nearest bus stop
		nearestBusStopName = ""
		nearestBusStopDistance = None


		for busStop in busStops:

			# Calculate the distance from the point to the bus stop
			busStopDistance = distance_a_b(point, busStop["location"])

			# If this is the first bus stop or if this bus stop is nearer than the previous nearest bus stop, set this bus stop as the nearest
			if nearestBusStopDistance == None or busStopDistance < nearestBusStopDistance:
				nearestBusStopName = busStop["name"]
				nearestBusStopDistance = busStopDistance


		# Store the nearest bus stop for each bus
		nearestBusStops[bus] = {
			"name":		nearestBusStopName,
			"distance":	nearestBusStopDistance
		}

	return nearestBusStops

def calculate_bus_stop_distance(busesDict, bus, busStopA, busStopB):

	# Find the position of the bus stop in the bus route
	busRoute = [busStop["name"] for busStop in busesDict[bus]["bus route"]]
	noOfA = busRoute.index(busStopA)
	noOfB = busRoute.index(busStopB)

	noOfBusStops = len(busRoute)


	# If busStopB is after busStopA
	if noOfB >= noOfA:
		return noOfB - noOfA


	# If busStopB is before busStopA
	else:
		# Bus loops to reach busStopA
		if busesDict[bus]["loops"]:
			return noOfB - noOfA + noOfBusStops

		# Impossible to reach busStopA
		else:
			return None

def calculate_minimum_travel_time(busesDict, pointA, pointB):

	travelTimes = []


	# Get the dictionaries of the nearest bus stops to pointA & pointB
	busStopsA = get_nearest_bus_stops(busesDict, pointA)
	busStopsB = get_nearest_bus_stops(busesDict, pointB)


	# Calculate the travel time of walking from pointA to pointB
	distance = distance_a_b(pointA, pointB)

	walkingTime = distance / AVERAGE_WALKING_SPEED

	travelTimes.append([walkingTime, "walking"])


	# Calculate the travel time of taking a bus from pointA to pointB
	for bus in busesDict:

		# Add time of walking to the bus stops & waiting for the bus
		travelTime = (busStopsA[bus]["distance"] + busStopsB[bus]["distance"]) / AVERAGE_WALKING_SPEED + BUS_WAITING_TIME

		# Add bus ride time
		busStopDistance = calculate_bus_stop_distance(busesDict, bus, busStopsA[bus]["name"], busStopsB[bus]["name"])

		# If this bus route is possible, add it to the travelTimes dictionary
		if busStopDistance != None:
			travelTime += busStopDistance * BUS_STOP_TIME
			travelTimes.append([travelTime, bus, busStopsA[bus]["name"], busStopsB[bus]["name"]])
	
	# Find the route with the shortest travel time
	miniumumTravelTime = min(travelTimes, key = itemgetter(0))

	return miniumumTravelTime


# Query Functions (Yee Teng & Tiffany)
def list_canteens(database):
	list_of_canteens = []

	for i in database:
		list_of_canteens.append(i)

	return list_of_canteens

def list_stalls(database, canteen):
	list_of_stalls = []

	for i in database:
		if canteen == i:
			for j in database[i]['stalls']:
				list_of_stalls.append(j)

	return list_of_stalls

def list_stallfood(database, canteen, stall):
	list_of_food = []
	
	for i in database:
		if canteen == i:
			for j in database[i]['stalls']:
				if stall == j:
					for food in database[i]['stalls'][j]['food']:
						food_info = database[i]['stalls'][j]['food'][food]
						food_info_list = [food, food_info["price"]]

						if food_info["halal"]:
							food_info_list.append("Halal")
						if food_info["vegetarian"]:
							food_info_list.append("Vegetarian")
						list_of_food.append(food_info_list)

	return list_of_food

def list_cuisine(database):
	list_of_cuisine = []
	
	for i in database:
		for j in database[i]['stalls']:
			list_of_cuisine.extend(database[i]['stalls'][j]["type"])

	list_of_cuisine = list(set(list_of_cuisine))

	return list_of_cuisine

def list_food(database):
	list_of_food = []
	
	for i in database:
		for j in database[i]['stalls']:
			for food in database[i]['stalls'][j]['food']:
				list_of_food.append(food)

	list_of_food = list(set(list_of_food))

	return list_of_food


# Sort Functions (Yanli & Tiffany)
def sort_rank(database, list_of_canteens = None):
	# creat list_of_ranking according to average votes of each canteen
	list_of_ranking = []
	sum_of_vote = 0
	number_of_stalls = 0

	if list_of_canteens == None:
		list_of_canteens = database.keys()

	for i in list_of_canteens:
		for j in database[i]["stalls"]:
			sum_of_vote = sum_of_vote + database[i]["stalls"][j]["votes"]
			number_of_stalls += 1
		ave_vote = sum_of_vote/number_of_stalls
		list_of_ranking.append([i, ave_vote])

	#sort the rank and return the name of the canteen
	sort_info = sorted(list_of_ranking, key = itemgetter(1))
	sort_info.reverse()
	canteen_rank = []

	for i in range(len(sort_info)):
		canteen_rank.append(sort_info[i][0])

	return canteen_rank

def sort_distance(database, location_of_users, list_of_canteens = None):
	list_of_distance = []

	if list_of_canteens == None:
		list_of_canteens = database.keys()

	for i in list_of_canteens:
		name_of_canteen = i
		location_of_canteen = database[i]["location"]
		distance_of_canteen = distance_a_b(location_of_users, location_of_canteen)
		list_of_distance.append([name_of_canteen, distance_of_canteen])

	sort_info = sorted(list_of_distance, key = itemgetter(1))

	return sort_info

def sort_travel_time(database, busesDict, location_of_users, list_of_canteens = None):
	# Create a list of the travel times from the user's location to each canteen
	list_of_travel_time = []

	if list_of_canteens == None:
		list_of_canteens = database.keys()

	for i in list_of_canteens:
		name_of_canteen = i		
		location_of_canteen = database[i]["location"]

		travel_time_of_canteen = calculate_minimum_travel_time(busesDict, location_of_users, location_of_canteen)
		list_of_travel_time.append([name_of_canteen] + travel_time_of_canteen)


	# Sort by travel time (shortest to longest)
	sort_info = sorted(list_of_travel_time, key = itemgetter(1))

	return sort_info

def sort_price(database, list_of_canteens = None):
	list_of_price = []

	if list_of_canteens == None:
		list_of_canteens = database.keys()
	
	for i in list_of_canteens:
		sum_of_price = 0
		number_of_food = 0

		for j in database[i]["stalls"]:
			for foodname in database[i]["stalls"][j]["food"]:
				sum_of_price += database[i]["stalls"][j]["food"][foodname]["price"]
				number_of_food += 1

		ave_price = sum_of_price / number_of_food
		list_of_price.append([i, ave_price])

	sort_info = sorted(list_of_price, key = itemgetter(1))

	return sort_info


# Search Functions (Yee Teng & Yanli)
def search_by_price(foodInfo, low, high):
	stalls_in_range = []

	for i in foodInfo:
		if low <= i[3] <= high:
			stalls_in_range.append(i)

	return stalls_in_range

def search_by_food(foodInfo, food):
	stalls_with_food = []

	for i in foodInfo:
		if i[2] == food:
			stalls_with_food.append(i)

	return stalls_with_food

def search_by_cuisine(database, cuisine):
	list_of_cuisine = []

	for i in database:
		for j in database[i]['stalls']:
			for k in database[i]['stalls'][j]['type']:
				if cuisine == k:
					list_of_cuisine.append([i, j])

	return list_of_cuisine

def search_by_foodrequirement(database, requirement):
	list_of_canteens = []

	for i in database:
		for j in database[i]['stalls']:
			for k in database[i]['stalls'][j]['food']:
				if database[i]['stalls'][j]['food'][k][requirement] == True:
					list_of_canteens.append([i,j])
					break

	return list_of_canteens


# Update Functions (Yanli)
def update_location(canteen, new_location):
	with open("canteens.json", "r") as canteensFile:
		data = json.load(canteensFile)

	data[canteen]["location"] = new_location

	with open("canteens.json", "w") as canteensFile:
		json.dump(data, canteensFile)

	global canteensDict
	canteensDict = data

def update_vote(canteen, stall_update):
	with open("canteens.json", "r") as canteensFile:
		data = json.load(canteensFile)

	original_votes = data[canteen]["stalls"][stall_update]["votes"]
	data[canteen]["stalls"][stall_update]["votes"] = original_votes + 1

	with open("canteens.json", "w") as canteensFile:
		json.dump(data, canteensFile)

	global canteensDict
	canteensDict = data

def update_price(canteen, stall_update, food_update, price_update):
	with open("canteens.json", "r") as canteensFile:
		data = json.load(canteensFile)

	# original_price = data[canteen]["stalls"][stall_update]["food"][food_update]["price"]
	data[canteen]["stalls"][stall_update]["food"][food_update]["price"] = price_update

	with open("canteens.json", "w") as canteensFile:
		json.dump(data, canteensFile)

	global canteensDict
	canteensDict = data

	global foodInfo
	foodInfo = load_food_info(canteensDict)


# Main App Option Functions (All)
def query_canteens():

	def query_canteens_option():

		# Display the location of the canteens
		def display_map():
			locations = locations_of_canteens(canteensDict, canteens)
			display_locations(locations, numbered = True)

		# Display the list of canteens
		canteens = list_canteens(canteensDict)
		display_list("List of Canteens", canteens, additionalButton = ["Display on Map", display_map], numbered = True)

	def query_stalls_option():

		# Display the list of stalls
		def display_stalls_list(canteen):
			stalls = list_stalls(canteensDict, canteen)
			display_list("List of Stalls in " + canteen, stalls)

		# Display the canteens as buttons
		canteens = list_canteens(canteensDict)

		options = []

		for canteen in canteens:
			options.append([canteen, lambda canteen = canteen : display_stalls_list(canteen)])

		display_options("In Which Canteen?", options)

	def query_stallfood_option():

		def display_stall_options(canteen):

			# Display the list of stall food
			def display_food_list(stall):
				food = list_stallfood(canteensDict, canteen, stall)
				display_table("List of Food in " + stall, food, ["Food", "Price ($)", "Remarks"])

			# Display the stalls as buttons
			stalls = list_stalls(canteensDict, canteen)

			options = []

			for stall in stalls:
				options.append([stall, lambda stall = stall : display_food_list(stall)])

			display_options("In Which Stall?", options)

		# Display the canteens as buttons
		canteens = list_canteens(canteensDict)
		title = "In Which Canteen?"

		options = []

		for canteen in canteens:
			options.append([canteen, lambda canteen = canteen : display_stall_options(canteen)])

		display_options(title, options)

	def query_cuisine_option():
		# Display the list of cuisine
		cuisines = list_cuisine(canteensDict)
		display_list("List of Cuisine", cuisines)

	def query_food_option():
		# Display the list of food
		foods = list_food(canteensDict)
		display_list("List of Food", foods)

	def query_travel_route_option():
		# Get the user's location
		user_location = get_location()

		if user_location == None:
			messagebox.showerror("Error", "No location clicked")
		else:
			def display_travel_route(canteen):
				travelTimeInfo = calculate_minimum_travel_time(busesDict, user_location, canteensDict[canteen]["location"])

				# Walking Route
				if travelTimeInfo[1] == "walking":
					def directions():
						canteenLocation = canteensDict[canteen]["location"]
						display_locations([canteenLocation], user_location)

					display_table("Fastest Travel Route to " + canteen, [travelTimeInfo], ["Travel Time (min)", "Route"], additionalButton = ["Directions", directions])
					
				# Bus Route (points out which bus stops to get on & off at, as well as the destination)
				else:
					def directions():
						busRoute = [busStop["name"] for busStop in busesDict[travelTimeInfo[1]]["bus route"]]
						noOfA = busRoute.index(travelTimeInfo[2])
						noOfB = busRoute.index(travelTimeInfo[3])
						busStopA = busesDict[travelTimeInfo[1]]["bus route"][noOfA]["location"]
						busStopB = busesDict[travelTimeInfo[1]]["bus route"][noOfB]["location"]
						canteenLocation = canteensDict[canteen]["location"]
						display_locations([busStopA, busStopB, canteenLocation], user_location, numbered = True)

					display_table("Fastest Travel Route to " + canteen, [travelTimeInfo], ["Travel Time (min)", "Route", "From", "To"], additionalButton = ["Directions", directions])

			# Display the canteens as buttons
			canteens = list_canteens(canteensDict)

			options = []

			for canteen in canteens:
				options.append([canteen, lambda canteen = canteen : display_travel_route(canteen)])

			display_options("Which Canteen Do You Want to Go to?", options)				

	def query_open_option():
		# Get the current time
		current_time = datetime.datetime.now().time()

		time_format = "%Y-%m-%d %H:%M:%S"

		# Compile the opening hours of the canteens with the datetime.time object for comparison
		list_of_open = []

		for i in canteensDict:
			open_time_str = canteensDict[i]["opening time"]
			open_time = datetime.datetime.strptime(open_time_str, time_format).time()
			close_time_str = canteensDict[i]["closing time"]
			close_time = datetime.datetime.strptime(close_time_str, time_format).time()

			if open_time <= current_time <= close_time:
				list_of_open.append([i, "Open"])
			else:
				list_of_open.append([i, "Closed"])

		# Display whether the canteens are open or closed
		display_table("Which Canteens Are Open at " + current_time.strftime("%H:%M:%S"), list_of_open, ["Canteen", "Now"])

	title = "Query"

	options = [
		["Canteens",						query_canteens_option],
		["Stalls in Canteens",				query_stalls_option],
		["Food in Stalls",					query_stallfood_option],
		["Cuisine",							query_cuisine_option],
		["Food",							query_food_option],
		["Travel Route to Canteen",			query_travel_route_option],
		["Which Canteens Are Open Now?",	query_open_option]
	]

	display_options(title, options)

def sort_canteens(list_of_canteens = None):

	# If not sorting after a search, set the default list_of_canteens to all canteens
	if list_of_canteens == None:
		list_of_canteens = canteensDict.keys()

	def sort_rank_option():
		# Sort the canteens by rank & display them in a list & map
		def display_map():
			locations = locations_of_canteens(canteensDict, sorted_rank)
			display_locations(locations, numbered = True)

		sorted_rank = sort_rank(canteensDict, list_of_canteens)
		display_list("Ranking of Canteens", sorted_rank, numbered = True, additionalButton = ["Display on Map", display_map])
	
	def sort_distance_option():
		# Sort the canteens by distance & display them in a table & map
		user_location = get_location()

		if user_location == None:
			messagebox.showerror("Error", "No location clicked")
		else:
			def display_map():
				locations = locations_of_canteens(canteensDict, canteen_list_from_2D_list(sorted_dist))
				display_locations(locations, user_location, numbered = True)

			sorted_dist = sort_distance(canteensDict, user_location, list_of_canteens)
			display_table("Nearest Canteens by Distance", sorted_dist, ["Canteen", "Distance (m)"], numbered = True, additionalButton = ["Display on Map", display_map])

	def sort_travel_time_option():
		# Sort the canteens by travel time & display them in a table & map
		user_location = get_location()

		if user_location == None:
			messagebox.showerror("Error", "No location clicked")
		else:
			def display_map():
				locations = locations_of_canteens(canteensDict, canteen_list_from_2D_list(sorted_travel))
				display_locations(locations, user_location, numbered = True)

			sorted_travel = sort_travel_time(canteensDict, busesDict, user_location, list_of_canteens)
			display_table("Nearest Canteens by Travel Time", sorted_travel, ["Canteen", "Travel Time (min)", "Route", "From", "To"], numbered = True, additionalButton = ["Display on Map", display_map])

	def sort_average_price_option():
		# Sort the canteens by average price & display them in a table & map
		def display_map():
			locations = locations_of_canteens(canteensDict, canteen_list_from_2D_list(sorted_price))
			display_locations(locations, numbered = True)

		sorted_price = sort_price(canteensDict, list_of_canteens)
		display_table("Canteens with the Cheapest Food", sorted_price, ["Canteen", "Average Price ($)"], numbered = True, additionalButton = ["Display on Map", display_map])

	title = "Sort Canteens By"

	options = [
		["Rank",			sort_rank_option],
		["Distance",		sort_distance_option],
		["Travel Time",		sort_travel_time_option],
		["Average Price",	sort_average_price_option],
	]

	display_options(title, options)

def search_canteens():

	def search_cuisine_option():
		# Display the stalls that serve the cuisine
		def display_cuisine(cuisine):
			stalls = search_by_cuisine(canteensDict, cuisine)
			list_of_canteens = list(set(canteen_list_from_2D_list(stalls)))
			display_table("Where You Can Find " + cuisine, stalls, ["Canteen", "Stall"], additionalButton = ["Sort", lambda : sort_canteens(list_of_canteens)])

		# Display the cuisines as buttons
		cuisines = list_cuisine(canteensDict)

		options = []

		for cuisine in cuisines:
			options.append([cuisine, lambda cuisine = cuisine : display_cuisine(cuisine)])

		display_options("Which Cuisine Would You Like", options)

	def search_food_option():
		# Display the canteens that serve the food
		def display_food(food):
			canteens_with_food = search_by_food(foodInfo, food)
			list_of_canteens = list(set(canteen_list_from_2D_list(canteens_with_food)))
			display_table("Where You Can Find " + food, canteens_with_food, ["Canteen", "Stall", "Food", "Price"], additionalButton = ["Sort", lambda : sort_canteens(list_of_canteens)])

		# Display the food as buttons
		foodList = list_food(canteensDict)

		options = []

		for food in foodList:
			options.append([food, lambda food = food : display_food(food)])

		display_options("Which Food Would You Like", options, small = True)

	def search_price_option():
		# Display the food in the price range if any
		def display_food_in_range(priceRange):
			validPrice = price_validate(priceRange[0]) and price_validate(priceRange[1])

			if not validPrice:
				tkinter.messagebox.showerror("Error", "Please enter non-negative numbers")
			else:
				low = float(priceRange[0])
				high = float(priceRange[1])

				food_in_range = search_by_price(foodInfo, low, high)

				if food_in_range == []:
					tkinter.messagebox.showerror("Error", "Sorry, no canteens sell food within that range")
				else:
					list_of_canteens = list(set(canteen_list_from_2D_list(food_in_range)))
					display_table("List of Food in Price Range", food_in_range, ["Canteen", "Stall", "Food", "Price"], numbered = False, additionalButton = ["Sort", lambda : sort_canteens(list_of_canteens)])

		display_entries("Price Range", ["Lowest Price: ", "Highest Price: "], display_food_in_range)

	def search_price_and_food_option():

		# Display the food in the price range if any as buttons
		def display_food_in_range(priceRange):
			validPrice = price_validate(priceRange[0]) and price_validate(priceRange[1])

			if not validPrice:
				tkinter.messagebox.showerror("Error", "Please enter non-negative numbers")
			else:
				low = float(priceRange[0])
				high = float(priceRange[1])

				food_in_range = search_by_price(foodInfo, low, high)

				if food_in_range == []:
					display_list("Where You Can Find " + food, ["Sorry, no canteen in our database sells food within that price range"])
				else:
					# Display the canteens that sell the food in the price range
					def display_food(food):
						canteens_with_food = search_by_food(food_in_range, food)
						list_of_canteens = list(set(canteen_list_from_2D_list(canteens_with_food)))
						display_table("Where You Can Find " + food, canteens_with_food, ["Canteen", "Stall", "Food", "Price"], additionalButton = ["Sort", lambda : sort_canteens(list_of_canteens)])

					foodList = []

					for food in food_in_range:
						foodList.append(food[2])

					foodList = list(set(foodList))

					options = []

					for food in foodList:
						options.append([food, lambda food = food : display_food(food)])

					display_options("Which Food Would You Like", options, small = True)

		display_entries("Price Range", ["Lowest Price: ", "Highest Price: "], display_food_in_range)

	def search_food_requirements_option():

		# Display the stalls that serve food that meets the food requirement
		def display_food_requirement(food_requirement):
			stalls_with_requirement = search_by_foodrequirement(canteensDict, food_requirement.lower())

			if stalls_with_requirement == []:
				display_list("List of Stalls with " + food_requirement + " Food", ["Sorry, no stall in our database sells " + food_requirement + " food"])
			else:
				list_of_canteens = list(set(canteen_list_from_2D_list(stalls_with_requirement)))
				display_table("List of Stalls with " + food_requirement + " Food", stalls_with_requirement, ["Canteen", "Stall"], additionalButton = ["Sort", lambda : sort_canteens(list_of_canteens)])

		options = [
			["Halal",		lambda : display_food_requirement("Halal")],
			["Vegetarian",	lambda : display_food_requirement("Vegetarian")]
		]

		display_options("What's Your Food requirement", options)

	title = "Search Canteens By"

	options = [
		["Cuisine",				search_cuisine_option],
		["Food",				search_food_option],
		["Price",				search_price_option],
		["Price & Food",		search_price_and_food_option],
		["Food Requirements",	search_food_requirements_option]
	]

	display_options(title, options)	

def update_canteens():

	def update_canteen(canteen):
		
		def update_location_option():
			# Update the location of the canteen
			new_location = get_location()

			if new_location == None:
				messagebox.showerror("Error", "No location clicked")
			else:
				update_location(canteen, new_location)
				display_list("Update Successful", ["The location of " + canteen + " has been updated", "Thank you for your information"])

		def update_stalls_option():

			def update_stall(stall):

				# Vote for the stall
				def update_vote_option():
					update_vote(canteen, stall)
					display_list("Vote Successful", ["Thank you for voting for " + stall])

				# Update the price of the food in the stall
				def update_food_option():

					def display_update_food_price(food):

						# Update the price of the food if valid price
						def update_food_price(prices):
							new_price_str = prices[0]

							if not price_validate(new_price_str):
								tkinter.messagebox.showerror("Error", "Please enter a non-negative number")
							else:
								new_price_float = float(new_price_str)
								update_price(canteen, stall, food, new_price_float)
								display_list("Update Successful", ["The price of " + food + " has been updated", "Thank you for your information"])


						display_entries(food, ["New Price: "], update_food_price)


					# Display the food as buttons
					foodList = list_stallfood(canteensDict, canteen, stall)

					options = []

					for food in foodList:
						foodName = food[0]
						options.append([foodName, lambda food = foodName : display_update_food_price(foodName)])

					display_options("Which Food's Price Would You Like to Update", options)


				options = [
					["Vote for This Stall",					update_vote_option],
					["Update Price of Food",				update_food_option]
				]

				display_options("What Would You Like to Update in " + stall, options)

			# Display stalls as buttons
			stalls = list_stalls(canteensDict, canteen)

			options = []

			for stall in stalls:
				options.append([stall, lambda stall = stall : update_stall(stall)])

			display_options("Which Stall to Update in " + canteen, options)


		title = "Which Information to Update in " + canteen

		options = [
			["Location",	update_location_option],
			["Stalls",		update_stalls_option]
		]	

		display_options(title, options)


	# Display the canteens as buttons
	canteens = list_canteens(canteensDict)

	options = []

	for canteen in canteens:
		options.append([canteen, lambda canteen = canteen : update_canteen(canteen)])

	display_options("Which Canteen to Update", options)


# Main GUI Functions (All)
MAX_BUTTONS_PER_COLUMN = 7
MAX_LABELS_PER_COLUMN = 15
frames = []

def canteen_list_from_2D_list(aList):
	# Converts a 2D list with additional info to just a list of the canteens inside with no repetitions
	return [i[0] for i in aList]

def price_validate(priceStr):
	# Returns True if the priceStr is a non-negative float
	try:
		priceFloat = float(priceStr)

		if priceFloat >= 0:
			return True
		else:
			return False

	except ValueError:
		return False

def display_no_canteens(title, message):
	frame = new_frame()

	# Create a title
	titleLabel = tkinter.Label(frame, text = title, height = 3, font = TITLE_FONT)
	titleLabel.pack()

	label = tkinter.Label(frame, text = message, height = 1, font = NORMAL_FONT)
	label.pack()

	spaceLabel = tkinter.Label(frame)
	spaceLabel.pack()

	quitButton = tkinter.Button(frame,
						text = "Quit",
						width = 50,
						height = 3,
						font = NORMAL_FONT,
						command = quit)
	quitButton.pack()

def display_main_options(title, options):

	# Display the title, main option buttons & a quit button

	frame = new_frame()

	# Create a title
	titleLabel = tkinter.Label(frame, text = title, height = 3, font = TITLE_FONT)
	titleLabel.pack()

	# Create a buttons frame
	buttonsFrame = tkinter.Frame(frame)
	buttonsFrame.pack()

	# Add options
	for i in range(len(options)):
		button = tkinter.Button(buttonsFrame,
						text = options[i][0],
						width = 50,
						height = 3,
						font = NORMAL_FONT,
						command = options[i][1])
		button.grid(row = i % MAX_BUTTONS_PER_COLUMN, column = i // MAX_BUTTONS_PER_COLUMN, padx = 5, pady = 5)

	# Add a space
	spaceLabel = tkinter.Label(frame)
	spaceLabel.pack()

	# Add a quit button
	quitButton = tkinter.Button(frame,
						text = "Quit",
						width = 50,
						height = 3,
						font = NORMAL_FONT,
						command = quit)
	quitButton.pack()

	return frame

def display_options(title, options, small = False):

	# Display the title, the option buttons & a back button
	# small = True if you want smaller option buttons

	frame = new_frame()

	# Create a title
	titleLabel = tkinter.Label(frame, text = title, height = 3, font = TITLE_FONT)
	titleLabel.pack()

	# Create a buttons frame
	buttonsFrame = tkinter.Frame(frame)
	buttonsFrame.pack()

	# Add options
	for i in range(len(options)):
		if small:
			button = tkinter.Button(buttonsFrame,
						text = options[i][0],
						width = 30,
						height = 2,
						font = SMALL_FONT,
						command = options[i][1])
			button.grid(row = i % int(MAX_BUTTONS_PER_COLUMN // 0.75), column = i // int(MAX_BUTTONS_PER_COLUMN // 0.75), padx = 5, pady = 5)
		else:
			button = tkinter.Button(buttonsFrame,
							text = options[i][0],
							width = 50,
							height = 3,
							font = NORMAL_FONT,
							command = options[i][1])
			button.grid(row = i % MAX_BUTTONS_PER_COLUMN, column = i // MAX_BUTTONS_PER_COLUMN, padx = 5, pady = 5)

	# Add a space
	spaceLabel = tkinter.Label(frame)
	spaceLabel.pack()

	# Add a back button
	backButton = tkinter.Button(frame,
						text = "Back",
						width = 50,
						height = 3,
						font = NORMAL_FONT,
						command = back)
	backButton.pack()

	return frame

def display_list(title, aList, numbered = False, additionalButton = None):
	
	# Display the title, the list (with numbers if numbered = True), (an additional button if assigned) and a back button

	frame = new_frame()

	# Create a title
	titleLabel = tkinter.Label(frame, text = title, height = 3, font = TITLE_FONT)
	titleLabel.pack()

	# Create a list frame
	listFrame = tkinter.Frame(frame)
	listFrame.pack()

	# Add list lines
	for i in range(len(aList)):
		if numbered:
			text = str(i + 1) + ". "+ aList[i]
		else:
			text = aList[i]
		label = tkinter.Label(listFrame, text = text, height = 1, font = NORMAL_FONT)
		label.grid(row = i % MAX_LABELS_PER_COLUMN, column = i // MAX_LABELS_PER_COLUMN)

	# Add a space
	spaceLabel = tkinter.Label(frame)
	spaceLabel.pack()

	# Add an addition button
	if additionalButton:

		button = tkinter.Button(frame,
						text = additionalButton[0],
						width = 50,
						height = 2,
						font = SMALL_FONT,
						command = additionalButton[1])
		button.pack()

	# Add a Back Button
	backButton = tkinter.Button(frame,
						text = "Back",
						width = 50,
						height = 2,
						font = SMALL_FONT,
						command = back)
	backButton.pack()

def display_table(title, aList, headers, numbered = False, additionalButton = None, startingNum = 0):

	# Display the title, the table of aList(with headers & numbers if numbered = True), (an additional button if assigned) and a back button
	# startingNum used if there's too many items to fit on one page & you want to continue on the next with numbering

	frame = new_frame()

	# Create a title
	titleLabel = tkinter.Label(frame, text = title, height = 3, font = TITLE_FONT)
	titleLabel.pack()

	# Create a list frame
	listFrame = tkinter.Frame(frame)
	listFrame.pack()

	# Add headers
	if numbered:
		headers.insert(0, "No.")

	for i in range(len(headers)):
		label = tkinter.Label(listFrame, text = headers[i], height = 1, font = BOLD_FONT)
		label.grid(row = 0, column = i)

	# Add rows
	for i in range(min(len(aList), MAX_LABELS_PER_COLUMN)):

		if numbered:
			label = tkinter.Label(listFrame, text = startingNum + i + 1, height = 1, font = NORMAL_FONT)
			label.grid(row = i + 1 % MAX_LABELS_PER_COLUMN, column = 0)

		for j in range(len(aList[i])):
			if isinstance(aList[i][j], float):
				text = str(round(aList[i][j], 2))
			else:
				text = str(aList[i][j])

			label = tkinter.Label(listFrame, text = text, height = 1, font = NORMAL_FONT)

			if numbered:
				label.grid(row = i + 1, column = j + 1)
			else:
				label.grid(row = i + 1, column = j)

	# Add a space
	spaceLabel = tkinter.Label(frame)
	spaceLabel.pack()

	# Add an additional button
	if additionalButton:

		button = tkinter.Button(frame,
						text = additionalButton[0],
						width = 50,
						height = 2,
						font = SMALL_FONT,
						command = additionalButton[1])
		button.pack()

	# Add a more button if too many items to fit on one page
	if len(aList) > MAX_LABELS_PER_COLUMN:

		def more():
			if numbered:
				headers.remove("No.")
			display_table(title, aList[MAX_LABELS_PER_COLUMN : ], headers, numbered, additionalButton, startingNum + MAX_LABELS_PER_COLUMN)

		moreButton = tkinter.Button(frame,
						text = "More",
						width = 50,
						height = 2,
						font = SMALL_FONT,
						command = more)
		moreButton.pack()

	# Add a back Button
	backButton = tkinter.Button(frame,
						text = "Back",
						width = 50,
						height = 2,
						font = SMALL_FONT,
						command = back)
	backButton.pack()

	return frame

def display_entries(title, inputs, action):
	frame = new_frame()

	# Create a title
	titleLabel = tkinter.Label(frame, text = title, height = 3, font=TITLE_FONT)
	titleLabel.pack()

	# Create entries
	inputsFrame = tkinter.Frame(frame)
	inputsFrame.pack()

	answersVars = []

	for i in range(len(inputs)):

		# Create a label
		inputLabel = tkinter.Label(inputsFrame, text = inputs[i], height = 3, font = BOLD_FONT)
		inputLabel.grid(row = i, column = 0)

		# Create an entry
		answerVar = tkinter.StringVar()
		answersVars.append(answerVar)

		inputEntry = tkinter.Entry(inputsFrame, width = 20, font = NORMAL_FONT, textvariable = answerVar)
		inputEntry.grid(row = i, column = 1)

	def activate_action():

		answers = []

		for answerVar in answersVars:
			answer = answerVar.get()
			answers.append(answer)

		action(answers)

	# Add a space
	spaceLabel = tkinter.Label(frame)
	spaceLabel.pack()

	# Create an Submit button
	submitButton = tkinter.Button(frame,
							text = "Submit",
							width = 50,
							height = 2,
							font = SMALL_FONT,
							command = activate_action)
	submitButton.pack()

	# Add a Back Button
	backButton = tkinter.Button(frame,
								text = "Back",
								width = 50,
								height = 2,
								font = SMALL_FONT,
								command = back)
	backButton.pack()

	return frame

def back():
	# Removes the current frame from the frames list & replaces the current frame with the previous frame
	currentFrame = frames.pop()
	currentFrame.pack_forget()
	prevFrame = frames[-1]
	prevFrame.pack()

def quit():
	# Closes the application
	global running
	running = False
	root.destroy()

def new_frame():
	# Creates a new frame, adds it to the list of frames & makes it replace the current frame

	if frames:
		currentFrame = frames[-1]
		currentFrame.pack_forget()

	frame = tkinter.Frame(root)
	frame.pack()
	frames.append(frame)

	return frame


# Main App (All)
# Create the root
root = tkinter.Tk()
root.title("NTU Canteen Recommender")

screenWidth = root.winfo_screenwidth()
screenHeight = root.winfo_screenheight()
root.geometry("{}x{}".format(screenWidth, screenHeight))
root.resizable(0, 0)

# Fonts
NORMAL_FONT_SIZE = screenHeight * 0.015
SMALL_FONT = tkinter.font.Font(family = "Helvetica", size = round(NORMAL_FONT_SIZE * 0.75))
NORMAL_FONT = tkinter.font.Font(family = "Helvetica", size = round(NORMAL_FONT_SIZE))
BOLD_FONT = tkinter.font.Font(family = "Helvetica", size = round(NORMAL_FONT_SIZE), weight = "bold")
TITLE_FONT = tkinter.font.Font(family = "Helvetica", size = round(NORMAL_FONT_SIZE * 1.5), weight = "bold")

# Create Main Frame
title = "NTU Canteen Recommender"

# If no canteens
if canteensDict == {}:
	message = "Sorry, there are no canteens in our database"
	display_no_canteens(title, message)

# If canteens, display the main options
else:
	options = [
		["Query Canteens",		query_canteens],
		["Sort Canteens",		sort_canteens],
		["Search Canteens",		search_canteens],
		["Update Canteens",		update_canteens],
	]

	display_main_options(title, options)

# Handle window closing (check if window closed manually or by mouse click)
running = True
root.protocol("WM_DELETE_WINDOW", quit)

# Keep the window open as long as it's not closed manually or by mouse click
while running:
	root.update_idletasks()
	root.update()