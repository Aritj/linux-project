import os
import json
import asyncio
from kasa.smartplug import SmartPlug, DeviceType, SmartDevice, requires_update

def reboot():
	''' Reboots the server '''
	os.system("sudo reboot")

def refreshIPs():
	''' Calls bash script to scan network for plugs '''
	os.system("../bash-scripts/get_plug_ip.sh")

# Refresh IPs whenever connector.py is run (python3 connector.py) or imported (python3 app.py)
refreshIPs()

def refreshStats():
	''' Refresh server stats '''
	os.system('../bash-scripts/cpu-memory-swap.sh') # localhost
	os.system('ssh serverAlex "./cpu-memory-swap.sh" >> data/server.txt') # external host
	os.system('ssh serverArnie "./cpu-memory-swap.sh" >> data/server.txt') # external host

def getServerInfo():
	''' Returns text in "server.txt" as list '''
	with open('data/server.txt', 'r') as r:
		list = []
		text = r.read()
		for line in text.splitlines():
			list.append(line)
	return(list)

def getPlugInfo():
	''' Returns a dictionary with Alias, IP, MAC, Model and Is_on values for each plug '''
	with open('data/ip.txt', 'r') as r:
		next(r) # skip header/subnet info
		text = r.read()
		full_dict = {}
		linecount = 0
		for ip in text.splitlines():
			linecount += 1
			plug = SmartPlug(ip)
			asyncio.run(plug.update())
			plug_dict = {
				'Alias': plug.alias,
				'IP_address': ip,
				'MAC_address': plug.mac,
				'RSSI': plug.rssi,
				'Model_nr': plug.model,
				'Is_on': str(plug.is_on),
				'Emeter_realtime': plug.emeter_realtime,
				'Emeter_today': plug.emeter_today,
				'Emeter_month': plug.emeter_this_month
				}
			full_dict.update({linecount:plug_dict})
	return full_dict

def getMoreInfo(dict = getPlugInfo()):
	''' Function for retrieving more info (useless!!!) '''
	infoDict = {}
	for i in dict:
		ip = dict[i]['IP_address']
		plug = SmartPlug(ip)
		asyncio.run(plug.update())
		infoDict.update({i:plug.hw_info})
	return infoDict

def switchState(alias, dict = getPlugInfo()):
	''' Checks the state of given plug (given by plug Alias), and switches that state, very much like a simple on/off switch '''
	for i in dict:
		if dict[i]['Alias'] == alias:
			if dict[i]['Is_on'] == "True":
				print(asyncio.run(SmartPlug(dict[i]['IP_address']).update()))
				print(asyncio.run(SmartPlug(dict[i]['IP_address']).turn_off()))
			else:
				asyncio.run(SmartPlug(dict[i]['IP_address']).update())
				asyncio.run(SmartPlug(dict[i]['IP_address']).turn_on())

def activateAll(dict = getPlugInfo()):
	''' Loops through all plugs in the network '''
	''' and turns them back on, if they're off '''
	for i in dict:
		if dict[i]['Is_on'] == "False":
			asyncio.run(SmartPlug(dict[i]['IP_address']).update())
			asyncio.run(SmartPlug(dict[i]['IP_address']).turn_on())

def shutdownAll(dict = getPlugInfo()):
	''' Loops through all plugs in the network '''
	''' and turns them off, if they're online  '''
	for i in dict:
		if dict[i]['Is_on'] == "True":
			asyncio.run(SmartPlug(dict[i]['IP_address']).update())
			asyncio.run(SmartPlug(dict[i]['IP_address']).turn_off())

def writeDict(dict = getPlugInfo()):
	''' Writes raw JSON data to "hs100_data.json" under "templates" folder. '''
	with open('templates/hs100_data.json', 'w') as w:
		json.dump(dict, w, ensure_ascii = False)
	return dict

def readDict(dict = getPlugInfo()):
	''' Reads the JSON data stored under "hs100_data.json" '''
	with open('templates/hs100_data.json', 'r') as r:
		text = (json.dumps(json.load(r), ensure_ascii=False, indent = 4))
	return text

def formatJSON(dict = getPlugInfo()):
	''' Only for pretty printing, call for example "print(formatJSON(GetPlugInfo()))" '''
	return json.dumps(dict, ensure_ascii = False, indent = 4)
