from database.utils.manage import ManageInterface
from database.common.models import History
from database.connection import db, connect_to_database

connect_to_database()
db.create_tables([History])

db_manage = ManageInterface()
