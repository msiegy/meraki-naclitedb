#!/usr/bin/python
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS
import time
import threading
import os
from dotenv import load_dotenv
import meraki

""" 
    - Create and Populate SQLite3 Database with endpoints
    - Run flask with API endpoints for updating and reading endpoint database.
    - When updating Endpoint API check if endpoint has passed crowdstrike or not and react with meraki GP client update API call for the appropriate group policy.

"""

load_dotenv()
MerakiAPIKey = os.environ.get('MerakiAPIKey')
network_id = os.environ.get('networkId')


def connect_to_db():
    conn = sqlite3.connect('database.db')
    return conn


def create_db_table():
    try:
        conn = connect_to_db()
        conn.execute('''DROP TABLE endpoints''')
        conn.execute('''
            CREATE TABLE endpoints (
                endpoint_id INTEGER PRIMARY KEY NOT NULL,
                name TEXT,
                mac_addresses TEXT NOT NULL,
				brand TEXT NOT NULL,
				location_code TEXT NOT NULL,
                crowdstrike	TEXT
            );
        ''')
        conn.commit()
        print("endpoint table created successfully")
    except:
        print("endpoint table creation failed - Maybe table")
    finally:
        conn.close()

def insert_endpoint(endpoint):
    inserted_endpoint = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO endpoints (mac_addresses, brand, location_code, crowdstrike, name) VALUES (?, ?, ?, ?, ?)", (endpoint['mac_addresses'], endpoint['brand'], endpoint['location_code'], endpoint['crowdstrike'], endpoint['name']) )
        conn.commit()
        inserted_endpoint = get_endpoint_by_id(cur.lastrowid)
    except:
        conn().rollback()

    finally:
        conn.close()

    return inserted_endpoint

def get_endpoints():
    endpoints = []
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM endpoints")
        rows = cur.fetchall()

        # convert row objects to dictionary
        for i in rows:
            endpoint = {}
            endpoint["endpoint_id"] = i["endpoint_id"]
            endpoint["name"] = i["name"]
            endpoint["mac_addresses"] = i["mac_addresses"]
            endpoint["brand"] = i["brand"]
            endpoint["location_code"] = i["location_code"]
            endpoint["crowdstrike"] = i["crowdstrike"]
            endpoints.append(endpoint)

    except:
        endpoints = []

    return endpoints

def get_endpoint_by_id(endpoint_id):
    endpoint = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM endpoints WHERE endpoint_id = ?", (endpoint_id,))
        row = cur.fetchone()

        # convert row object to dictionary
        endpoint["endpoint_id"] = row["endpoint_id"]
        endpoint["name"] = row["name"]
        endpoint["mac_addresses"] = row["mac_addresses"]
        endpoint["brand"] = row["brand"]
        endpoint["location_code"] = row["location_code"]
        endpoint["crowdstrike"] = row["crowdstrike"]
    except:
        endpoint = {}

    return endpoint

def get_endpoint_by_mac(endpoint_mac):
    endpoint = {}
    try:
        conn = connect_to_db()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM endpoints WHERE mac_addresses = ?", (endpoint_mac,))
        row = cur.fetchone()

        # convert row object to dictionary
        endpoint["endpoint_id"] = row["endpoint_id"]
        endpoint["name"] = row["name"]
        endpoint["mac_addresses"] = row["mac_addresses"]
        endpoint["brand"] = row["brand"]
        endpoint["location_code"] = row["location_code"]
        endpoint["crowdstrike"] = row["crowdstrike"]
    except:
        endpoint = {}

    return endpoint

def update_endpointbyID(endpoint):
    updated_endpoint = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE endpoints SET brand = ?, location_code = ?, crowdstrike = ? WHERE endpoint_id =?", (endpoint["brand"], endpoint["location_code"], endpoint["crowdstrike"], endpoint["endpoint_id"],))
        conn.commit()
        #return the endpoint
        updated_endpoint = get_endpoint_by_id(endpoint["endpoint_id"])

    except:
        conn.rollback()
        updated_endpoint = {}
    finally:
        conn.close()

    return updated_endpoint

def update_endpointbyMAC(endpoint):
    updated_endpoint = {}
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("UPDATE endpoints SET brand = ?, location_code = ?, crowdstrike = ? WHERE mac_addresses =?", (endpoint["brand"], endpoint["location_code"], endpoint["crowdstrike"], endpoint["mac_addresses"],))
        conn.commit()
        #return the endpoint
        updated_endpoint = get_endpoint_by_mac(endpoint["mac_addresses"])

    except:
        conn.rollback()
        updated_endpoint = {}
    finally:
        conn.close()

    return updated_endpoint

def check_endpointstatus(endpoint):
    #check endpoint crowdstrike value and return
    endpoint_record = get_endpoint_by_mac(endpoint)
    if endpoint_record["crowdstrike"] == "PASSED":
        print("\nendpoint - " + endpoint + " passed crowdstrike, value = " + endpoint_record["crowdstrike"] + "\n Client GP updated to TRUSTED via Meraki API\n")
        updateclientPolicy(endpoint, 104)
        return True
    else:
        print("\nendpoint - " + endpoint + "  did NOT pass crowdstrike, value = " + endpoint_record["crowdstrike"] + "\n Client GP updated to REMEDIATE via Meraki API\n")
        updateclientPolicy(endpoint, 102)
        return False

def updateclientPolicy(endpoint, policy_id):
    dashboard = meraki.DashboardAPI(MerakiAPIKey, suppress_logging=True)
    endpointmac = ':'.join(endpoint[i:i+2] for i in range(0,12,2))
    response = dashboard.networks.updateNetworkClientPolicy(
    network_id, endpointmac, 'Group policy', 
    groupPolicyId=policy_id
)

endpoints = []
endpoint0 = {
    "mac_addresses": "AA240909039F",
    "name": "DALXR-Printer02",
    "brand": "Fairfield Inn",
    "location_code": "LABR1",
    "crowdstrike": "PASSED"
}

endpoint1 = {
    "mac_addresses": "BB240909039F",
    "name": "DALXR-PoS02",
    "brand": "Fairfield Inn",
    "location_code": "LABR1",
    "crowdstrike": ""
}
endpoint2 = {
    "mac_addresses": "CC240909039F",
    "name": "DALXR-GREDOCSIS1",
    "brand": "Fairfield Inn",
    "location_code": "LABR1",
    "crowdstrike": "FAILED"
}
endpoint3 = {
    "mac_addresses": "b827ebf2d773",
    "name": "FamilyRoom-OSMC-PI",
    "brand": "Fairfield Inn",
    "location_code": "CABMIL1",
    "crowdstrike": "PASSED"
}

endpoints.append(endpoint0)
endpoints.append(endpoint1)
endpoints.append(endpoint2)
endpoints.append(endpoint3)

create_db_table()

for i in endpoints:
    print(insert_endpoint(i))



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/api/endpoints', methods=['GET'])
def api_get_enpoints():
    return jsonify(get_endpoints())

@app.route('/api/endpoints/<endpoint_id>', methods=['GET'])
def api_get_endpointbyid(endpoint_id):
    return jsonify(get_endpoint_by_id(endpoint_id))

@app.route('/api/endpoints/mac/<endpoint_mac>', methods=['GET'])
def api_get_endpointbymac(endpoint_mac):
    return jsonify(get_endpoint_by_mac(endpoint_mac))

@app.route('/api/endpoints/add',  methods = ['POST'])
def api_add_endpoint():
    endpoint = request.get_json()
    return jsonify(insert_endpoint(endpoint))

@app.route('/api/endpoints/updatebyid',  methods = ['PUT'])
def api_update_endpointbyid():
    endpoint = request.get_json()
    return jsonify(update_endpointbyID(endpoint))

@app.route('/api/endpoints/updatebymac',  methods = ['PUT'])
def api_update_endpointbymac():
    endpoint = request.get_json()
    if endpoint['crowdstrike'] == "PASSED":
        updateclientPolicy(endpoint["mac_addresses"], 104)
        print("\n>endpoint - " + endpoint["mac_addresses"] + " passed crowdstrike, value = " + endpoint["crowdstrike"] + "\n>>> Client GP updated to TRUSTED via Meraki API\n")
    else:
        updateclientPolicy(endpoint["mac_addresses"], 102)
        print("\n>endpoint - " + endpoint["mac_addresses"] + "  did NOT pass crowdstrike, value = " + endpoint["crowdstrike"] + "\n>>> Client GP updated to REMEDIATE via Meraki API\n")
    return jsonify(update_endpointbyMAC(endpoint))

@app.route('/api/endpoints/delete/<endpoint_id>',  methods = ['DELETE'])
def api_delete_endpoint(endpoint_id):
    return jsonify(delete_endpoint(endpoint_id))

#Start Flask Server and sample loop to continuously check endpoint status
if __name__ == "__main__":
    #app.debug = True
    #app.run(debug=False)
    #app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)).start()

'''
    starttime = time.time()
    while True:
        check_endpointstatus("b827ebf2d773")
        print("--tick--")
        time.sleep(15.0 - ((time.time() - starttime) % 15.0))
'''