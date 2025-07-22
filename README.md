# 🌤️ Tropical Cloud Detection

A sophisticated satellite data processing platform for cloud detection using INSAT-3DR satellite imagery. Built with Django and deployed on Google Cloud Platform.

## ✨ Features

### 🚀 Enhanced User Experience
- **Smooth Loading Animations**: Beautiful progress bars with shimmer effects
- **Real-time Processing Status**: Live updates with detailed progress tracking
- **Drag & Drop Upload**: Intuitive file upload interface
- **Responsive Design**: Works seamlessly on all devices

### 🔬 Advanced Processing
- **INSAT-3DR Algorithm**: Original confidential cloud detection algorithm
- **Large File Support**: Handles files up to 100MB efficiently
- **Memory Optimization**: Intelligent processing for large datasets
- **Multi-format Support**: HDF5, NetCDF, and other satellite formats

### ☁️ Cloud Infrastructure
- **Google Cloud Storage**: Secure file storage and retrieval
- **Auto-scaling**: Handles variable load with 1-10 instances
- **High Performance**: 4 CPU cores, 16GB RAM configuration
- **Fast Processing**: 2-5 minutes for 50MB files

## 🏗️ Architecture

### Current Configuration
- **CPU**: 4.0 vCPUs
- **Memory**: 16GB RAM
- **Storage**: 20GB disk
- **Workers**: 3 workers with 4 threads each
- **Timeout**: 15 minutes per request

### Processing Pipeline
1. **File Upload** (30-60s): Secure upload to Google Cloud Storage
2. **Data Extraction** (15-30s): HDF5 file reading and validation
3. **Algorithm Processing** (60-120s): Cloud detection with morphological filtering
4. **Visualization** (30-60s): Plot generation and result storage
5. **Results Storage** (15-30s): Database updates and file management

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Cloud Platform account
- Django 3.2+

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/TropicalCloudDetection.git
   cd TropicalCloudDetection
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your configuration
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start development server**
   ```bash
   python manage.py runserver
   ```

## 🎨 Enhanced Loading Experience

### Upload Progress
- **Smooth Animations**: Cubic-bezier easing for natural feel
- **Step-by-step Progress**: Detailed status updates
- **Visual Feedback**: Shimmer effects and color transitions
- **Error Handling**: Graceful error animations

### Processing Status
- **Real-time Updates**: Auto-refresh every 5 seconds
- **Progress Visualization**: Animated progress bars
- **Step Indicators**: Clear processing stage display
- **Log Streaming**: Live processing logs

### Animation Features
- **Fade-in Effects**: Smooth element transitions
- **Scale Animations**: Responsive visual feedback
- **Loading Spinners**: Professional loading indicators
- **Success/Error States**: Clear status communication

## 📁 Project Structure

```
TropicalCloudDetection/
├── cloud_detection/          # Main Django app
│   ├── templates/           # HTML templates
│   ├── static/             # Static files (CSS, JS, images)
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── processing.py       # Processing pipeline
│   └── insat_algorithm.py  # Original algorithm
├── static/                 # Global static files
│   ├── css/               # Enhanced loading animations
│   └── js/                # Interactive JavaScript
├── media/                 # User uploads and results
├── requirements.txt        # Python dependencies
├── app.yaml              # Google App Engine config
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables
```bash
ENVIRONMENT=production
DEBUG=False
GCS_BUCKET_NAME=your-bucket-name
GOOGLE_CLOUD_PROJECT=your-project-id
```

### Google Cloud Setup
1. Enable required APIs:
   - Cloud Run API
   - Cloud Build API
   - Storage API

2. Create GCS bucket for uploads
3. Set up service account with appropriate permissions

## 📊 Performance Metrics

### Processing Times (50MB file)
- **Best Case**: ~2 minutes
- **Average Case**: ~3-4 minutes
- **Worst Case**: ~5 minutes

### Resource Usage
- **Memory**: Optimized for large files
- **CPU**: Efficient multi-threading
- **Network**: Optimized GCS transfers

## 🛠️ Development

### Adding New Features
1. Create feature branch
2. Implement changes
3. Test thoroughly
4. Update documentation
5. Submit pull request

### Testing
```bash
python manage.py test
```

### Code Style
- Follow PEP 8
- Use meaningful variable names
- Add comprehensive comments
- Include docstrings

## 🚀 Deployment

### Google App Engine
```bash
gcloud app deploy
```

### Cloud Run
```bash
./deploy-cloud-run.sh
```

### Manual Deployment
```bash
./quick-deploy.sh
```

## 📈 Monitoring

### Cloud Console
- Monitor CPU and memory usage
- Track request latency
- View error rates
- Analyze traffic patterns

### Application Logs
- Processing status updates
- Error tracking
- Performance metrics
- User activity logs

## 🔒 Security

### Data Protection
- Secure file uploads
- Encrypted storage
- Access control
- Audit logging

### Best Practices
- No sensitive data in code
- Environment variable usage
- Regular security updates
- Input validation

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- INSAT-3DR satellite data processing team
- Google Cloud Platform for infrastructure
- Django community for the framework
- Open source contributors

## 📞 Support

For questions or issues:
- Create an issue on GitHub
- Check the documentation
- Review the logs
- Contact the development team

---

**Last Updated**: December 2024
**Version**: 2.0.0
**Status**: Production Ready ✅