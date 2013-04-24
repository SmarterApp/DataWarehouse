#!/usr/bin/python
# python edware_users_csv_to_ldif.py edware_header.ldif edware_users.csv edware_users.ldif
# jbecker@wgen.net
import psycopg2     # import postgres support
import csv          # imports the csv module
import sys          # imports the sys module

# main
def main():
    debug = 1
    users_in_role = []
    
    if len(sys.argv) != 4:
        print ("Invalid Number of Arguments, Missing HEADER, DATA and/or DEST file(s).")
        exit()
    
    try:
        conn = psycopg2.connect("dbname='edware' user='edware' host='edwdbsrv1' password='edware2013'")
        cur1 = conn.cursor()
    except:
        print ("Unable to connect to the database.")
        exit()
    
    try:    
        sql1 = "CREATE TABLE IF NOT EXISTS public.buffer_csv (GUID varchar(100),name varchar(100),email varchar(100), " + \
                      "userid varchar(100),password varchar(100),sys_role varchar(100),district varchar(100)," + \
                      "state varchar(100),row varchar(100),_column varchar(100),NOTES varchar(100));"
        cur1.execute(sql1)
        cur1.execute("DELETE FROM public.buffer_csv;")
        conn.commit()
    except conn.DatabaseError, e:
        print ("Unable to create buffer table.")
        close_handles()
        exit()
    
    try:
        f_header = open(sys.argv[1], 'rU') # opens the header csv file
        #f_user = open(sys.argv[2], 'rU') # opens the user csv file
        f_dest = open(sys.argv[3], 'w') # opens the destination csv file
    except IOError:
        print ("Unable to open HEADER/DEST files.")
        exit()
    
    try:
        dump_header(f_header, f_dest)
        
        with open(sys.argv[2],'rU') as user_data: # `with` statement available in 2.5+
            # csv.DictReader uses first line in file for column headings by default
            dr = csv.DictReader(user_data) # comma is default delimiter
            to_db = [(unicode(ix['GUID'],"utf8"),unicode(ix['name'],"utf8"),unicode(ix['email'],"utf8"),unicode(ix['userid'],"utf8"),unicode(ix['password'],"utf8"), \
                    unicode(ix['sys_role'],"utf8"),unicode(ix['district'],"utf8"),unicode(ix['state'],"utf8"),unicode(ix['row'],"utf8"), \
                    unicode(ix['_column'],"utf8"),unicode(ix['NOTES'],"utf8")) for ix in dr]   
    
        #GUID,name,email,userid,password,sys_role,district,state,row,_column,NOTES            
        sql2 = " INSERT INTO public.buffer_csv " + \
        " ( GUID, name, email, userid, password, sys_role, district, state, row, _column, NOTES ) " + \
        " VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s );"
        
        if (debug):
            print sql2
        
        #jsbiii 20130423
        cur1.executemany(sql2, to_db)
        conn.commit()
                    
        sql3 = "SELECT name, email, userid, password, sys_role " + \
               "FROM public.buffer_csv " + \
               "ORDER BY sys_role"
        
        cur1.execute(sql3)
        
        rows = cur1.fetchall()
        
        sys_role = ""
        for row in rows:
            if (debug):
                print ("\n", row[0], row[4])
                
            if(sys_role <> "" and sys_role <> row[4]):
                dump_roles(sys_role, users_in_role, f_dest)
                users_in_role = [ ]
                sys_role = row[4]
            else:
                sys_role = row[4]
            
            add_user_role(row[0], users_in_role)
            dump_user(row[0], row[2], row[3], f_dest)
     
        dump_roles(sys_role, users_in_role, f_dest)
                 
        print ("Edware CSV2LDIF Conversion Complete!")                
    except IOError as e:  
        print "unable to open DATA file."
        exit()
        
# library functions
def add_user_role(_user, _users_in_role):
    _users_in_role.append(_user) 

def close_handles():
    f_header.close()            # closing header file
    f_user.close()              # closing data file
    f_dest.close()              # closing data file
    conn.close()                # closing db connection 

def dump_header(_file_header, _file_dest):
    try:
       _file_dest.write(_file_header.read())
    except:
        print("Unable to write header.")
        exit()

def dump_user(_user, _uid, _passwd, _file_dest):
    try:
        user = format_inetOrgPerson(_user, _uid, _passwd)
        _file_dest.write(user)
    except:
        print("Unable to write user.")
        exit()

def dump_roles(_sys_role, _user_roles, _file_dest):
    try:
        group = format_groupOfNames(_sys_role, _user_roles)
        _file_dest.write(group)
    except:
        print("Unable to write roles.")
        exit()
    
def format_inetOrgPerson(_user, _uid, _passwd):
    user = _user.split(' ')
    if (len(user) > 2):
        fname = user[0]
        lname = user[2]
    else:
        fname, lname = _user.split(' ' , 2 )
        
    strInetOrgPerson =  "dn: cn="+_user+",ou=people,ou=environment,dc=edwdc,dc=net\n" + \
                        "objectClass: inetOrgPerson\n" + \
                        "objectClass: top\n" + \
                        "cn: " + _user + "\n" + \
                        "sn: " + lname + "\n" + \
                        "givenName: " + fname + "\n" + \
                        "uid: " + _uid + "\n" + \
                        "userPassword: " + _passwd + "\n"

    return strInetOrgPerson + "\n"

def format_groupOfNames(_group, _user_roles):
    strGroupOfNames = "cn="+ _group +",ou=groups,ou=environment,dc=edwdc,dc=net\n" + \
                      "objectClass: groupOfNames\n" + \
                      "objectClass: top\n" + \
                      "cn="+ _group + "\n"
    
    for user in _user_roles:
        strGroupOfNames += "member: cn=" + user + ",ou=people,ou=environment,dc=edwdc,dc=net\n"
        
    return strGroupOfNames + "\n"

if __name__ == "__main__":
    main()
