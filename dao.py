
import MySQLdb
import subprocess

import train_num

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
    try:
	if len(song_title) == 0:
            return ""
	return song_title[0][0]
    except:
        return ""

def get_num_songs():
    sql = """select COUNT(*) from tracks"""
    return int(db_select(sql, params=None)[0][0])


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

# Make this return actual recommendations
def get_song_recommendations(song_id):
    print(song_id)
    #if song_id == None:
    #    return None
    result=train_num.main(song_id)
    result=map(lambda id: (id, get_song_title(id)), result[0])
    print result
    return result
