import sys
import os
import psycopg2
import time



def find_from_num_ip(num_address, rows):
    max_value = len(rows)
    id_temp = max_value/2
    min_value = 0
    #k=0
    while  1 :
        if num_address < rows[id_temp][0]:
            max_value = id_temp
            id_temp = (id_temp + min_value)/2
            #k= k + 1
        elif num_address > rows[id_temp+1][0]:
            min_value = id_temp
            id_temp = (id_temp + max_value)/2
            #k = k + 1
        else:
            #print k
            return id_temp



if __name__=='__main__':
    conn = psycopg2.connect("dbname=iplocation user=postgres password='laffi14'")
    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("SELECT begin_num FROM ip_param;")
    rows = cur.fetchall()
    os.system('say -v Daniel "Gmail" &')
    this_time = time.time()
    ip_num_test = 988999999
    parameter = find_from_num_ip(ip_num_test, rows)
    print (time.time() - this_time)
    print (parameter)
    print (rows[parameter][0])
    print (ip_num_test)
    print (rows[parameter+1][0])


