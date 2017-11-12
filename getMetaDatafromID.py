import MySQLdb
import sys
import pandas as pd
mysql_cn= MySQLdb.connect(host='localhost', user='root',passwd='#Phard', db='classy')

def getFromDB(id, column):
	describe = pd.read_sql('describe tracks;', con = mysql_cn)
	print describe
	results = pd.read_sql('select ' + column +' from tracks where id =' + str(id), con = mysql_cn)
	print results
	if len(results) == 1 :
		return results
	elif len(results) == 0:
		print ("No " + column + " for id " + str(id))
		return ""
	else:
		print ("Multiple " + column + " for id " + str(id))
		return ""

def main(id):
	print (id, getFromDB(id, 'track_title'), getFromDB(id, 'artist_name'))
if __name__ == "__main__":
	main(sys.argv[1])
	
		
