# cse2102-fall2025-Team26

## Link to our Trello board: https://trello.com/invite/b/68d1a841b6cfcf676caacc5c/ATTIcedbbca74cc4ec14b8a556ae283879566F446268/kanban-board-group-project
## Link to our Figma: https://www.figma.com/design/4ootrp1KnmXadh6ZOWYpqk/Group-Project?node-id=0-1&t=Siv9Bbf4Ny0oeADz-1

# Sahana Ganesh
# Christopher Lambiase
# Joe Buchek
# Lakshita Ganesh Kumar

# RUNNING THE BACKEND LOCALLY
Open a new terminal
cd into the backend directory
Create virtual environment by running "python3 -m venv venv"
Activate venv by running "source venv/bin/activate"
cd back to the root directory by running "cd ../"
Install requirements by running "pip3 install -r requirements.txt"
Start the backend server by running "python3 backend/main.py"
Server will be running at port 5001 (the URL will be provided in the terminal)

# RUNNING THE FRONTEND LOCALLY
Open a new terminal
cd into the frontend directory
Start the frontend server by running "npm run dev"
Server will be running at port 5173 (the URL will be provided in the terminal)

# RUNNING THE BACKEND THROUGH DOCKER:
Make sure Docker Desktop is open
Open a new terminal
Build Docker Image: docker build -f Dockerfile --tag team26 .
Run Docker Image: docker run -p 5001:5001 team26

# RUNNING THE FRONTEND THROUGH DOCKER:
Make sure Docker Desktop is open
Open a new terminal
cd into the frontend directory
Build Docker Image: docker build -f Dockerfile --tag team26-frontend .
Run Docker Image: docker run -p 5173:5173 team26-frontend
