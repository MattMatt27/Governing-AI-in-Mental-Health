# Mental Health AI Bill Tracker

A Flask web application for tracking and analyzing state legislation related to AI in mental health services.

## Features

- **Search and Filter**: Search bills by state, bill number, or taxonomy code
- **Tag-based Filtering**: Filter bills by 25 different regulatory tags
- **Taxonomy Classification**: View bills categorized by their relevance to mental health AI
- **Interactive UI**: Modern, responsive interface with modal popups for definitions
- **Real-time Updates**: Connected to PostgreSQL database for live data

## Security Notice

This repository does not contain any sensitive information. Database credentials should be configured through environment variables.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mh-ai-bill-tracker.git
cd mh-ai-bill-tracker
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database URL for local development
```

5. Run the application locally:
```bash
python app.py
```

## Deployment on Railway

Railway is the recommended deployment platform for this application.

### Prerequisites
- A Railway account (sign up at https://railway.app)
- A GitHub account with this repository

### Deployment Steps

1. **Fork or push this repository to GitHub**

2. **Create a new project on Railway:**
   - Go to https://railway.app/new
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. **Add PostgreSQL database:**
   - In your Railway project, click "New Service"
   - Choose "Database" → "Add PostgreSQL"
   - Railway will automatically create the database

4. **Connect database to your app:**
   - Click on your app service
   - Go to "Variables" tab
   - Click "Add Reference Variable"
   - Select your PostgreSQL database
   - Choose `DATABASE_URL`
   - Railway will automatically inject the connection string

5. **Deploy:**
   - Railway will automatically deploy your app
   - Your app will be available at `https://your-app-name.railway.app`

### Environment Variables on Railway

Railway automatically provides:
- `DATABASE_URL` - PostgreSQL connection string (when you add the database)
- `PORT` - Port for your application

No manual configuration needed!

### Custom Domain (Optional)

1. In your Railway service settings, go to "Settings" → "Domains"
2. Add your custom domain
3. Update your DNS records as instructed

## Local Development

For local development with a remote Railway database:

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Link your project:
```bash
railway link
```

4. Run locally with Railway environment:
```bash
railway run python app.py
```

## Project Structure

```
mh-ai-bill-tracker/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── railway.toml          # Railway configuration
├── README.md             # Project documentation
├── .gitignore           # Git ignore file
├── static/              # Static files
│   ├── css/
│   │   └── style.css   # Custom styles
│   └── js/
│       └── main.js     # Frontend JavaScript
└── templates/          # HTML templates
    └── index.html      # Main page template
```

## API Endpoints

- `GET /` - Main web interface
- `GET /api/bills` - Get filtered bills data
- `GET /api/stats` - Get statistics
- `GET /api/states` - Get list of states
- `GET /health` - Health check endpoint

## Technologies Used

- **Backend**: Flask, PostgreSQL, psycopg2
- **Frontend**: HTML, Tailwind CSS, Vanilla JavaScript
- **Deployment**: Railway
- **Database**: PostgreSQL

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues or questions:
- Open an issue on GitHub
- Check Railway documentation at https://docs.railway.app
- Review Flask documentation at https://flask.palletsprojects.com