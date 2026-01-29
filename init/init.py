import psycopg2

if __name__ == "__main__":
    print("Logged Here!")
    con = psycopg2.connect(database="postgres", user='postgres', password='password', host='postgres', port=5432)
    cur = con.cursor()
    cur.execute('''
                CREATE TABLE if not exists public.hosts ( 
                    hostid serial primary key, 
                    name text, 
                    bio text, 
                    photo text 
                );  

                CREATE TABLE if not exists public.shows ( 
                    showid serial primary key, 
                    name text, 
                    starttime integer, 
                    endtime integer, 
                    weekday integer, 
                    description text, 
                    photo text 
                );   

                CREATE TABLE if not exists public.hostshowlink ( 
                    hostid integer, 
                    showid integer 
                ); 
                ''')
    con.commit()
    con.close()
