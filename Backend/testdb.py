from app.database import db, users_col
from app.config import MONGO_URI, DB_NAME

print("Connecting to:", MONGO_URI)
print("Using database:", DB_NAME)
print("Existing databases on this cluster:", db.client.list_database_names())
print("Collections in this database:", db.list_collection_names())
print("User count:", users_col.count_documents({}))