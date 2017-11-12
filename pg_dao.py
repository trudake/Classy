import MySQLdb


mysql_cn = MySQLdb.connect(host='quanta-rabi.mit.edu', user='root', psswd='#Phard', db='classy')
crsr = mysql_cn.cursor

#Get song name
def get_song_title(song_id):
  sql = 'select track_title from tracks where tack_id = :song_id;'
  crsr.execute(sql, {'song_id' : song_id})
  song_title = crsr.fetchall()
  return song_title[0][0]


mysql_cn.close()
  
	
