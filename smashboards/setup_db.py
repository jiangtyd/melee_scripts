import mysql.connector
from mysql.connector import errorcode
from config.config import Config

def create_tables(sql_file, mysql_config):
  cnx = mysql.connector.connect(**mysql_config)
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

def main():
  config = Config()
  mysql_config = {
    'user': config.get_db_user(),
    'password': config.get_db_password(),
    'host': config.get_db_host(),
    'database': config.get_db_name()
  }
  create_tables('schema.sql', mysql_config)

if __name__ == '__main__':
  main()
