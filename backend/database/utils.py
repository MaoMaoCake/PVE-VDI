import mariadb

def _create_conn(username, password, host, database, port=3306):
    try:
        conn = mariadb.connect(
            user=username,
            password=password,
            host=host,
            port=port,
            database=database
        )
        return conn
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None

def create_cursor():
    return _create_conn('username', 'password', '127.0.0.1', 'pve_vdi', port=33060).cursor()

def dbexecute(query: str):
    cur = create_cursor()
    cur.execute(query)
    return cur.fetchall()
