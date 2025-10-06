# Fantasy Premier League App with Built-in Model for Predicting Players' Fantasy Points

This project is a web application for predicting fantasy points in the Fantasy Premier League using a combination of a Spring Boot backend, Flask API, and a React frontend.

## Prerequisites

Make sure you have the following installed on your system:

- [Node.js](https://nodejs.org/) (for the frontend)
- [Java JDK 11+](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html) (for the Spring Boot backend)
- [Python 3](https://www.python.org/downloads/) (for the Flask API)
- [Maven](https://maven.apache.org/) (if you aren't using the provided `./mvnw` wrapper)

## Setup Instructions

### 1. Clone the Repository

Clone the repository from GitHub and navigate into the project directory.

git clone https://github.com/yourusername/fantasy-premier-league-app.git
cd fantasy-premier-league-app

### 2. Set Up the Frontend

Navigate to the frontend directory and install the necessary Node.js dependencies by running npm install.

To start the frontend development server, run npm start.

To build the production version of the frontend, run npm run build.

### 3. Set Up the Backend (Spring Boot)

Navigate to the backend directory.

If you're using the provided Maven wrapper, run ./mvnw spring-boot:run.

If you have Maven installed globally, run mvn spring-boot:run to start the Spring Boot application.

### 4. Set Up the Flask API (Python)

Navigate to the flask-api directory.

Create a virtual environment by running python3 -m venv venv, then activate the virtual environment.

On Linux/macOS, activate with source venv/bin/activate.
On Windows, use venv\Scripts\activate.

Once the virtual environment is active, install the required Python packages by running pip install -r requirements.txt.

To run the Flask API, execute python app.py.

### 5. Set Up Environment Variables

Some services may require configuration through environment variables. Ensure you set up the correct environment variables for each component:

Backend: Configure the backend/src/main/resources/application.properties file for database connections, API keys, or any sensitive data your backend requires.
Flask API: If the Flask API requires environment variables, create a .env file in the flask-api directory or update the necessary sections in app.py for your configuration (e.g., Flask secret keys, external API URLs).

### 6. Running the Entire Application

To start the entire project:

Start the Flask API
From the flask-api directory, ensure the virtual environment is activated, and run the Flask server using python app.py.

Start the Spring Boot Backend
From the backend directory, start the backend by running ./mvnw spring-boot:run (or mvn spring-boot:run if Maven is installed globally).

Start the React Frontend
From the frontend directory, run the command npm start to start the frontend server.

### 7. Accessing the Application

Once all services are running:

The React frontend should be accessible via http://localhost:3000 (or another port if configured).
The Spring Boot backend will likely run on http://localhost:8080 (or the port specified in your configuration).
The Flask API will be accessible via http://127.0.0.1:5000 (or the port configured for Flask).
Make sure all components are running and configured to communicate with each other properly (e.g., ensure the frontend is making the correct API calls to the backend and Flask API).

## Automated Data Ingestion

This project includes automated data ingestion via GitHub Actions that runs twice daily at 05:15 and 17:15 UTC to keep player data fresh.

### GitHub Actions Setup

1. **Repository Secrets**: Add the following secrets to your GitHub repository:
   - `DB_HOST`: MySQL host (default: localhost)
   - `DB_USER`: MySQL username (default: root)  
   - `DB_PASSWORD`: MySQL password (required)
   - `DB_NAME`: MySQL database name (default: fpl_optimization)

2. **Manual Trigger**: The workflow can be manually triggered from the Actions tab.

### What the ingestion does

1. Clones the FPL-Elo-Insights repository for additional data
2. Fetches fresh data from the official FPL API
3. Merges the data sources
4. Updates the MySQL database with fresh player statistics
5. Logs the ingestion run for monitoring

### Local Testing

To test the ingestion script locally:

```bash
cd flask-api
python scripts/test_ingest.py
```

Make sure to set the correct database credentials in the test script.

## Architecture

- **Frontend (React)**: User interface on port 3000
- **Spring Boot Backend**: Main API on port 8081, handles authentication and team management
- **Flask ML API**: Machine learning service on port 5001, handles optimization and predictions
- **MySQL Database**: Stores user data, teams, and player statistics
- **GitHub Actions**: Automated data ingestion twice daily
