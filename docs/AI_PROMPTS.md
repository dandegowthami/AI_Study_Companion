# AI Prompts Used During Development

## 1. Project Setup

- "I want to build a full stack AI study companion app. Backend in FastAPI + MongoDB, frontend in React + Vite. Help me set up the folder structure for both."
- "Set up a FastAPI project with routers, services, and a config file that reads from a .env file."
- "Add CORS middleware to FastAPI so my React frontend running on a different port can call the API."

## 2. Authentication

- "Add signup and login APIs using FastAPI. Use JWT for auth and bcrypt for password hashing."
- "How do I create a dependency in FastAPI that checks the JWT token and gives me the current user in every protected route?"
- "I need an admin role. Only users with role admin should be able to access certain routes, everyone else should get a 403."
- "On the frontend, create an AuthContext with login, signup and logout functions, and store the token in localStorage."
- "Add an axios interceptor that automatically attaches the JWT token to every request."

## 3. Spaces & Projects

- "Let users create Spaces (like subjects) and inside each Space, create Projects (like topics). Give me the MongoDB models and CRUD APIs."
- "Each space and project should belong to a user, so users can only see their own spaces and projects."
- "Make a React page to list all spaces as cards, and clicking a space shows its projects."

## 4. Material Upload & PDF Processing

- "Add an endpoint where a user can upload a PDF to a project. Extract text from the PDF using PyPDF2."
- "The PDF text needs to be chunked before embedding. Split it into chunks of around 500 words with some overlap so I don't lose context at chunk boundaries."
- "How do I keep track of which page a chunk came from, so later I can show 'Page 14' as a source?"
- "Processing a big PDF takes time, so run the extraction and embedding in a background task instead of blocking the upload request."
- "Add a status field (queued, processing, ready, failed) to materials and an endpoint the frontend can poll to check if processing is done."

## 5. Embeddings & Vector Search

- "I want to store embeddings so I can do semantic search over the uploaded material. Suggest a simple local vector database I can use without paying for a cloud service."
- "Use sentence-transformers to generate embeddings and store them in ChromaDB, one collection per project so materials don't mix between projects."
- "Write a search function that takes a question, embeds it, and returns the top 4 most similar chunks with their source page numbers."

## 6. AI Tutor (RAG)

- "I want to build a tutor chat feature where the AI only answers using the student's uploaded material, not its own general knowledge."
- "How do I set up Groq API in Python to call an LLM?"
- "Write a prompt that tells the model to answer only from the given context, and if the answer isn't in the context, reply with a fixed 'I don't have enough information' message."
- "If the vector search doesn't find anything relevant enough, don't even call the LLM, just return the fixed message directly to save cost."
- "Save each question and answer with its sources to MongoDB so the student can see their past conversations."

## 7. Concept Extraction & Mastery Tracking

- "After a PDF is processed, use the AI to read a sample of the text and pick out 4-6 main concepts covered in it."
- "For each concept, I want to track a mastery percentage. New concepts should start around 30%, not 0, since the student hasn't been tested yet."
- "When a student answers a quiz question right or wrong, increase or decrease their mastery for that concept. Harder questions should move the percentage more than easy ones."

## 8. Quiz Generation & Grading

- "Generate a quiz question using AI based on one of the student's concepts. Pick weaker concepts more often but don't always ask about the same one."
- "The question should be either multiple choice or open ended, and harder if the student's mastery is already high, easier if it's low."
- "For multiple choice, just compare the selected option, no need to call the AI for grading. For open ended answers, ask the AI to judge if the answer is correct and give short feedback."
- "Make a quiz session of 5 questions, then show the final score."

## 9. Analytics & Recommendations

- "Show the student their mastery trend per concept, whether they're improving, stable, or need to focus on it, based on their history."
- "After a quiz is completed, use AI to generate a short recommendation on what the student should focus on next, based on their concept trends."
- "Add a dashboard/home page showing overall progress, weak concepts, and recent projects."

## 10. Admin Dashboard

- "I want an admin panel to see all users, spaces, and projects across the whole platform, not just my own."
- "Add an AI usage page for admins showing how many AI calls were made, average response time, and estimated cost."
- "Every AI call should be logged with its feature name, latency, tokens used, and whether it succeeded or failed, so I can build this usage dashboard."
- "I don't have a labeled test set to evaluate the AI quality, so suggest some simple metrics I can calculate just from the logs I already have, like how often the tutor actually found a source vs said 'I don't know'."

## 11. Frontend Pages

- "Build the React pages for login, signup, spaces list, and project detail with tabs for Materials, Tutor, Quiz, and Analytics."
- "Style everything using Bootstrap since I don't have time to write custom CSS."
- "Add route protection so /home, /spaces, and /projects redirect to login if the user isn't logged in, and /admin redirects normal users away."

## 12. Debugging & Polish

- "My PDF upload sometimes returns empty text, how do I handle PDFs where text extraction fails?"
- "Getting a CORS error when calling the API from the frontend, how do I fix it?"
- "My JWT token expires too fast, how do I increase the expiry time?"
- "The admin activity tab isn't showing on the admin page, I think I forgot to add it to the tabs list."
