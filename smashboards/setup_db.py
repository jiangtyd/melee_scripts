import mysql.connector
from mysql.connector import errorcode
import db

def create_tables(sql_file, cnx):
  cursor = cnx.cursor()
  with open(sql_file, 'r') as fin:
    contents = fin.read()
    statements = contents.split(';')
    for statement in statements:
      if len(statement.strip()) == 0:
        continue
      try:
        print "Running statement {}".format(statement.strip())
        cursor.execute(statement)
      except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
          print("Error: table already exists.")
        else:
          print(err.msg)
      else:
        print("Success")

  cnx.commit()
  cursor.close()

def main():
  create_tables('schema.sql', db.get_connection())

if __name__ == '__main__':
  main()
