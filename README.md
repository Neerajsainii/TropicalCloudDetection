# Tropical Cloud Detection

A Django-based web application for processing and analyzing tropical cloud detection using INSAT-3DR satellite data. The application processes HDF5 satellite files and generates cloud coverage analysis with visualizations.

## 🌟 Features

- **Satellite Data Processing**: Handles INSAT-3DR L1B HDF5 files (up to 100MB)
- **Cloud Detection Algorithm**: Implements the original INSAT-3DR cloud detection algorithm
- **Real-time Processing**: Asynchronous file processing with background tasks
- **Interactive Dashboard**: Modern UI with real-time processing status
- **Data Visualization**: Generates cloud coverage plots and thumbnails
- **PostgreSQL Database**: Production-ready database for data persistence
- **Google Cloud Ready**: Optimized for Google Cloud Platform deployment

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL (for production)
- Google Cloud SDK (for deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TropicalCloudDetection
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main app: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## 🗄️ Database Configuration

### Local Development (SQLite)
The application uses SQLite by default for local development.

### Production (PostgreSQL)
For production deployment on Google Cloud:

1. **Set up PostgreSQL**
   ```bash
   # Using Google Cloud SQL
   gcloud sql instances create tropical-cloud-db \
       --database-version=POSTGRES_14 \
       --tier=db-f1-micro \
       --region=us-central1
   ```

2. **Configure database connection**
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

## 🌐 Deployment

### Google Cloud Platform

The application is optimized for Google Cloud Platform deployment with multiple options:

#### Option 1: Cloud Run (Recommended)
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT_ID/tropical-cloud-detection
gcloud run deploy tropical-cloud-detection \
    --image gcr.io/PROJECT_ID/tropical-cloud-detection \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

#### Option 2: App Engine
```bash
gcloud app deploy app.yaml
```

#### Option 3: Compute Engine
```bash
chmod +x gcp_deploy.sh
./gcp_deploy.sh
```

For detailed deployment instructions, see [README_GCP.md](README_GCP.md).

## 📁 Project Structure

```
TropicalCloudDetection/
├── cloud_detection/              # Main Django app
│   ├── models.py                 # Database models
│   ├── views.py                  # View logic
│   ├── processing.py             # Satellite data processing
│   ├── insat_algorithm.py        # Original INSAT algorithm
│   └── templates/                # HTML templates
├── cloud_detection_portal/       # Django project settings
│   ├── settings.py               # Application settings
│   └── urls.py                   # URL configuration
├── static/                       # Static files (CSS, JS, images)
├── media/                        # User uploads and results
├── requirements.txt              # Python dependencies
├── app.yaml                     # Google App Engine config
├── Dockerfile                   # Container configuration
└── README_GCP.md               # Google Cloud deployment guide
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Environment
ENVIRONMENT=production  # or 'local'
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@host:5432/database

# Security
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-domain.com

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com

# CSRF
CSRF_TRUSTED_ORIGINS=https://your-domain.com
```

### File Upload Settings

- **Maximum file size**: 100MB
- **Supported formats**: HDF5 (.h5) files
- **Processing timeout**: 5 minutes
- **Memory optimization**: Automatic for large files

## 📊 Features

### Satellite Data Processing

- **File Upload**: Drag-and-drop interface for HDF5 files
- **Validation**: Automatic file format and size validation
- **Processing**: Background processing with real-time status updates
- **Results**: Cloud coverage analysis and visualizations

### Dashboard Features

- **Processing Status**: Real-time progress tracking
- **Results Gallery**: Browse processed satellite data
- **Statistics**: Cloud coverage percentages and statistics
- **Geographic Data**: Latitude/longitude bounds and location names

### Admin Interface

- **Data Management**: View and manage uploaded files
- **Processing Logs**: Monitor processing status and errors
- **User Management**: Manage application users
- **System Monitoring**: View system statistics

## 🛠️ Development

### Running Tests

```bash
python manage.py test
```

### Code Quality

```bash
# Install development dependencies
pip install flake8 black isort

# Run linting
flake8 .
black .
isort .
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## 📈 Performance

### Optimization Features

- **Memory Management**: Automatic garbage collection for large files
- **Asynchronous Processing**: Background task processing
- **File Streaming**: Efficient handling of large satellite files
- **Database Optimization**: Connection pooling and query optimization

### Monitoring

- **Application Logs**: Comprehensive logging system
- **Performance Metrics**: Processing time and memory usage tracking
- **Error Handling**: Graceful error handling and recovery

## 🔒 Security

### Security Features

- **CSRF Protection**: Built-in Django CSRF protection
- **File Validation**: Secure file upload validation
- **SQL Injection Protection**: Django ORM protection
- **XSS Protection**: Template auto-escaping

### Production Security

- **HTTPS**: Automatic SSL termination (Cloud Run/App Engine)
- **Database Security**: Cloud SQL with connection encryption
- **Access Control**: Proper user authentication and authorization

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Documentation

- [Google Cloud Deployment Guide](README_GCP.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [Google Cloud Documentation](https://cloud.google.com/docs)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- INSAT-3DR satellite data processing algorithm
- Django web framework
- Google Cloud Platform infrastructure
- Scientific Python ecosystem (NumPy, Matplotlib, H5Py)

---

**Note**: This application is designed for processing tropical cloud detection data and is optimized for Google Cloud Platform deployment. For local development, SQLite is used by default, while PostgreSQL is recommended for production deployments.