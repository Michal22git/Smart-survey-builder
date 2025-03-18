# Smart Survey Builder

Smart Survey Builder is a full-stack app for generating and filling out surveys, utilizing OpenAI Structured Outputs. It consists of a Django-based backend and a React-based frontend.

## Backend

The backend is implemented in Django and provides a RESTful API for generating and managing surveys.

### Key Features

- Generating surveys based on templates and parameters using the OpenAI API
- Storing generated surveys in a PostgreSQL database
- Handling survey responses and storing them in the database
- Websocket for real-time communication during survey generation
- Survey analytics and report generation

### Project Structure

- `core/`: Django project configuration
- `openai_survey/`: Module for integration with the OpenAI API and survey generation
  - `SurveyGenerator`: Utilizes OpenAI language models like GPT-4 to generate survey questions and answer options based on a provided description
  - `SurveyProcessor`: Processes the generated survey, converting it to a format suitable for storing in the database
  - `SurveySchema`: Defines the data structure for generated surveys, ensuring data consistency and validation
- `survey/`: Django app for managing surveys and responses
- `survey_analytics/`: Module for survey analytics and report generation
  - `SurveyAnalyzer`: Performs analysis on survey responses, calculating statistics and generating summaries for each question
  - `SurveyVisualizer`: Creates data visualizations such as bar charts, pie charts, and word clouds based on the analysis results
  - `PDFExporter`: Exports the generated report to PDF format for easy sharing and archiving
  - `ReportGenerator`: Combines all components to generate a comprehensive survey analysis report, including summaries, visualizations, and detailed information

### Requirements

- Python 3.10
- Django 5.1
- Channels 4.0 (for WebSocket support)
- OpenAI API key

## Frontend

The frontend is built with React and provides a user interface for creating and filling out surveys.

### Key Features

- Interactive survey creation with AI-generated prompts
- Real-time survey preview during creation
- Survey filling by respondents
- Responsive design

### Project Structure

- `src/components/CreateSurvey/`: Components for creating surveys
- `src/components/FillSurvey/`: Components for filling out surveys
- `src/App.js`: Main application component
- `src/routes.js`: Routing configuration

### Requirements

- Node.js 19
- React 18

## Running the Application

### Using Docker Compose

1. Clone the repository
2. Make sure Docker is installed on your system
3. Navigate to the project's root directory
4. Run the command `docker-compose up`

The backend will be accessible at `http://localhost:8000`, and the frontend will be accessible at `http://localhost:3000`.

### Without Docker

1. Clone the repository
2. Backend:
   - Set environment variables in the `backend/.env` file (OpenAI API key, database access details)
   - Install dependencies: `pip install -r backend/requirements.txt`
   - Run database migrations: `python backend/manage.py migrate`
   - Start the server: `python backend/manage.py runserver`
3. Frontend:
   - Install dependencies: `npm install` (in the `frontend/` directory)
   - Start the application: `npm start`

The application will be accessible at `http://localhost:3000`.
