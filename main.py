import telnetlib
import time
import json

# Read configuration settings from config file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

gameservers = config['GameServers']
password = config['Password']
telnet_port = config['TelportPort']
seconds_to_check = config['SecondsToCheck']

# Function to hit telnet and get the status
def get_status(ip_address, port, password):
    try:
        tn = telnetlib.Telnet(ip_address, port)
        time.sleep(2)
        tn.read_until(b"Password: ")
        tn.write(password.encode('ascii') + b"\n")
        time.sleep(2)
        tn.write('status\n'.encode('ascii'))
        time.sleep(2)
        output = tn.read_very_eager().decode('ascii')
        tn.close()
        return output
    except Exception as e:
        print(f"Error occurred while connecting to {ip_address}: {e}")
        return None

# Do the thing
while True:
    results = {}
    for ip_data in gameservers:
        ip = ip_data['IP']
        name = ip_data['Name']
        output = get_status(ip, telnet_port, password)
        if output is not None:
            data = {
                'Status': 1,
                'RunningGame': None,
                'UsersInGame': None,
                'Name': name
            }
            lines = output.split('\r\n')
            for line in lines:
                if line.startswith('Current running game:'):
                    data['RunningGame'] = int(line.split(': ')[1])
                elif line.startswith('Current users in game:'):
                    data['UsersInGame'] = int(line.split(': ')[1])
            results[ip] = data
        else:
            results[ip] = {
                'Status': 0,
                'RunningGame': None,
                'UsersInGame': None,
                'Name': name
            }

    # Write results to a JSON file
    with open('results.json', 'w') as file:
        json.dump(results, file)

    # Extracting and printing desired fields
    for ip, data in results.items():
        status = "up" if data['Status'] == 1 else "down"
        running_game = data['RunningGame']
        users_in_game = data['UsersInGame']
        name = data['Name']

        print(f"Name: {name}")
        print(f"IP: {ip}")
        print(f"Status: {status}")
        print(f"Running Game: {running_game}")
        print(f"Users in Game: {users_in_game}")
        print()

    print("Telnet check completed.")