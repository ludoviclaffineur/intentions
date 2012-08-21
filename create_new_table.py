from googlemaps import GoogleMaps
import haversine
import sys
import psycopg2
import time

if __name__=='__main__':
    conn = psycopg2.connect("dbname=iplocation user=postgres password='laffi14'")

    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS ip_param, country_param ")
    conn.commit()
    #cur.execute("CREATE TABLE ip_param AS SELECT begin_num ,parameter FROM geoloc INNER JOIN country_param ON country_param.name_country = geoloc.name_country ")
    #conn.commit()