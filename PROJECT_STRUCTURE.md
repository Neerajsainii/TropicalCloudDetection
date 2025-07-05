# 🌟 Tropical Cloud Detection - Project Structure

## 📁 Project Organization

```
TropicalCloudDetection/
├── 🌐 frontend/                     # React TypeScript Frontend
│   ├── src/
│   │   ├── components/              # React Components
│   │   │   ├── ui/                  # shadcn/ui Components
│   │   │   ├── CloudAnalytics.tsx   # Analytics Dashboard
│   │   │   ├── SatelliteMap.tsx     # Satellite Visualization
│   │   │   ├── FileUpload.tsx       # File Upload Component
│   │   │   ├── RealTimeData.tsx     # Real-time Data Display
│   │   │   ├── ControlPanel.tsx     # Control Interface
│   │   │   ├── Header.tsx           # Navigation Header
│   │   │   └── HeroSection.tsx      # Landing Section
│   │   ├── pages/                   # Page Components
│   │   │   ├── Index.tsx            # Main Dashboard
│   │   │   └── NotFound.tsx         # 404 Page
│   │   ├── lib/                     # Utilities
│   │   │   ├── api.ts               # Backend API Service
│   │   │   └── utils.ts             # Helper Functions
│   │   ├── hooks/                   # React Hooks
│   │   └── styles/                  # CSS Styles
│   ├── package.json                 # Node.js Dependencies
│   ├── tailwind.config.ts           # Tailwind CSS Config
│   ├── vite.config.ts               # Vite Build Config
│   └── tsconfig.json                # TypeScript Config
│
├── 🔧 Backend (Django)
│   ├── cloud_detection/             # Main Django App
│   │   ├── models.py                # Database Models
│   │   ├── views.py                 # Django Views (Legacy)
│   │   ├── api_views.py             # REST API Endpoints
│   │   ├── serializers.py           # DRF Serializers
│   │   ├── processing.py            # Cloud Detection Logic
│   │   ├── admin.py                 # Django Admin
│   │   ├── urls.py                  # URL Routing
│   │   ├── forms.py                 # Django Forms (Legacy)
│   │   ├── migrations/              # Database Migrations
│   │   └── templates/               # Django Templates (Legacy)
│   │       └── cloud_detection/     # Template Files
│   │
│   ├── cloud_detection_portal/      # Django Project Settings
│   │   ├── settings.py              # Main Configuration
│   │   ├── urls.py                  # Root URL Configuration
│   │   ├── wsgi.py                  # WSGI Configuration
│   │   └── asgi.py                  # ASGI Configuration
│   │
│   ├── static/                      # Static Files (Legacy)
│   ├── media/                       # User Uploaded Files
│   ├── manage.py                    # Django Management Script
│   └── db.sqlite3                   # SQLite Database
│
├── 📦 Configuration
│   ├── requirements.txt             # Python Dependencies
│   ├── README.md                    # Project Documentation
│   ├── PROJECT_STRUCTURE.md         # This File
│   └── .gitignore                   # Git Ignore Rules
│
└── 🔄 Virtual Environment
    └── venv/                        # Python Virtual Environment
```

## 🎯 Key Components

### Frontend (React + TypeScript)
- **Modern UI**: Built with shadcn/ui components and Tailwind CSS
- **Real-time Updates**: Live data visualization and status monitoring
- **File Upload**: Drag-and-drop interface for satellite data files
- **Responsive Design**: Mobile-friendly satellite-themed interface

### Backend (Django + DRF)
- **REST API**: Full RESTful API for React frontend communication
- **File Processing**: HDF5/NetCDF satellite data processing
- **Database**: SQLite for development, PostgreSQL ready for production
- **Legacy Support**: Django templates maintained for backward compatibility

### Data Processing
- **Satellite Data**: HDF5 and NetCDF file format support
- **Cloud Detection**: Placeholder algorithms ready for your implementation
- **Visualization**: Matplotlib and Plotly for data visualization
- **Real-time**: Background processing with status tracking

## 🚀 Architecture

```
React Frontend (Port 5173)
      ↓ HTTP/REST API
Django Backend (Port 8000)
      ↓ File Processing
Cloud Detection Engine
      ↓ Results
Database + Media Files
```

## 📝 Development Notes

### Frontend
- Uses Vite for fast development and building
- TypeScript for type safety
- Tailwind CSS for styling
- React Query for data fetching
- Recharts for data visualization

### Backend
- Django 4.2.7 with REST Framework
- CORS enabled for React frontend
- File upload limit: 500MB
- Background processing support
- Admin interface available

### File Types Supported
- HDF5: `.h5`, `.hdf5`
- NetCDF: `.nc`, `.netcdf`
- Maximum file size: 500MB

## 🔧 Configuration

### Environment Variables
- `DEBUG`: Development mode toggle
- `SECRET_KEY`: Django secret key
- `ALLOWED_HOSTS`: Allowed hostnames
- `CORS_ALLOWED_ORIGINS`: Frontend URLs

### Database
- Development: SQLite
- Production: PostgreSQL/MySQL ready

## 📚 Legacy Files

The following files are maintained for backward compatibility:
- `cloud_detection/templates/` - Django HTML templates
- `cloud_detection/forms.py` - Django forms
- `cloud_detection/views.py` - Django views
- `static/` - Static files directory

These can be removed if you only plan to use the React frontend. 