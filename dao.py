
import MySQLdb

def get_connection():
    return MySQLdb.connect(
		user='root', 
		passwd='#Phard', 
		db='classy'
    )

def close_conn(conn):
    try:
        if (conn):
            conn.close()
    except:
        return

def db_select(sql, params):
    conn = get_connection()
    try:
        crsr = conn.cursor()
        crsr.execute(sql, params)
        return crsr.fetchall()
    finally:
        close_conn(conn)

#Get song name
def get_song_title(song_id):
    sql = """select track_title from tracks where ID = %s"""
    song_title = db_select(sql, (song_id,))
    return song_title[0][0]


# Find tracks with title matching term
def get_song_search_results(term):
    if not term:
        return None
    term = term.upper()
    sql = """select ID, track_title
             from tracks
             where upper(track_title) like %s
             limit 10
    """
    return db_select(sql, ('%' + term + '%',))

# TODO make this return actual recommendations
def get_song_recommendations(song_id):
    if song_id == None:
        return None
    return [
        (1865, 'Recommendation 1'),
        (4850, 'Recommendation 2'),
        (4851, 'Recommendation 3'),
        (5025, 'Recommendation 4')
    ]
