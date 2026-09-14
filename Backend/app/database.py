from pymongo import MongoClient
from app.config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

users_col = db["users"]
spaces_col = db["spaces"]
projects_col = db["projects"]
materials_col = db["materials"]
conversations_col = db["conversations"]
messages_col = db["messages"]
concepts_col = db["concepts"]
mastery_col = db["mastery"]
quiz_attempts_col = db["quiz_attempts"]
recommendations_col = db["recommendations"]
activity_col = db["activity"]
ai_logs_col = db["ai_logs"]
eval_results_col = db["eval_results"]