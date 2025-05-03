from tinydb import Query, TinyDB

db = TinyDB("db.json")
t_keyring = db.table("keyring")
t_user = db.table("user")

Q = Query()
