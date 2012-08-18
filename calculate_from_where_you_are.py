from googlemaps import GoogleMaps
import haversine
import sys
import psycopg2
import time


if __name__=='__main__':
    current_address = sys.argv[1]
    gmaps = GoogleMaps('AIzaSyDZBYwP1eT5HsOm7ztB2ELb250W_ktrmm8')
    coord_base = gmaps.address_to_latlng(current_address)

    conn = psycopg2.connect("dbname=iplocation user=postgres password='laffi14'")

    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT name_country FROM geoloc;")
    rows = cur.fetchall()
    distance_maxi = 20000.0
    for row in rows:
        print row
        if (row[0] != 'Anonymous Proxy' and row[0]!= 'Satellite Provider' and row[0] != 'Palestinian Territory, Occupied'):
            coord_current = gmaps.address_to_latlng(row)
            rapport = haversine.distance(coord_base, coord_current)/distance_maxi
            print(rapport)
            cur.execute("INSERT INTO country_param(name_country, parameter)  VALUES (%s, %s);", (row, rapport))
            conn.commit()
            time.sleep(1)