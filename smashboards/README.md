Setting up dependencies
======================
1. `mkdir env`
2. `virtualenv env`
3. `source env/bin/activate`
4. `pip install -r requirements.txt`

Setting up database
===================
1. Install mysql
2. Choose db name (example: `"swf"`)
3. In mysql: `CREATE TABLE swf`
4. Create `config/config.ini` with db host, username, password, and db name
5. `python setup_db.py`
