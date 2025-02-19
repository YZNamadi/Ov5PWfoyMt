#!/bin/bash

# Navigate to the backend directory and start the FastAPI server
cd backend
uvicorn main:app --reload &

# Navigate to the frontend directory and start the React app
cd ../frontend
npm start

# Wait for both processes to finish
wait
