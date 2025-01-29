Running the server:
$python main.py

Sending requests to the server:
$curl -X POST http://localhost:3000/api/page1/data -H "Content-Type: application/json" -d "{\"message\": \"value\"}"

run first:
$pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

TODO List
Dockerize the backend to ensure seamless deployment and scalability.
Integrate the LLM (Language Learning Model) connection for query processing.
Establish a secure and efficient connection to the database.
Define the interaction format between the frontend and backend.
Rename blueprints to align with finalized naming conventions.
