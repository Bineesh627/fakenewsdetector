# TruthGuard - Fake News Detector

A Django-based web application that uses machine learning (LSTM) to detect fake news from text or URLs. The platform provides real-time predictions, user authentication, admin management, and community feedback features.

## 🚀 Features

### For Users
- **Real-time Fake News Detection**: Analyze text or URLs using an LSTM-based ML model
- **User Authentication**: Sign up, login, and manage personal profiles
- **Profile Management**: Edit user information and change passwords
- **Community Voting**: Vote on predictions to help improve accuracy
- **Feedback System**: Submit corrections for false predictions
- **Prediction History**: View all predictions and their results

### For Admins
- **Admin Dashboard**: Comprehensive overview of system statistics
- **User Management**: Add, edit, delete users, and manage admin privileges
- **Activity Monitoring**: Track user activities and system events
- **Feedback Management**: Review and approve/reject user corrections
- **Prediction Management**: View, edit, and delete predictions
- **Export Data**: Export prediction data for analysis

## 🛠️ Technology Stack

### Backend
- **Django 4.2**: Web framework
- **Python 3.12**: Programming language
- **TensorFlow/Keras**: Machine learning framework
- **SQLite**: Database (default)

### Frontend
- **Bootstrap 5**: CSS framework
- **Bootstrap Icons**: Icon library
- **Tailwind CSS**: Utility-first CSS framework
- **Lucide Icons**: Icon library
- **SweetAlert2**: Beautiful alert popups
- **JavaScript**: Client-side interactivity

### Machine Learning
- **LSTM Model**: Long Short-Term Memory neural network for text classification
- **Tokenizer**: Text preprocessing for model input
- **Joblib**: Model and tokenizer serialization

## 📋 Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd fakenewsdetector
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv Scripts activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 7. Run the Development Server
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## 📁 Project Structure

```
fakenewsdetector/
├── detector/                 # Main application directory
│   ├── admin_views.py       # Admin panel views
│   ├── models.py            # Database models
│   ├── views.py             # User-facing views
│   ├── signals.py           # Django signals
│   ├── templates/           # HTML templates
│   │   ├── admin/           # Admin panel templates
│   │   ├── auth/            # Authentication templates
│   │   └── users/           # User-facing templates
│   └── static/              # Static files (CSS, JS)
├── fakenewsdetector/        # Django project configuration
│   ├── settings.py          # Project settings
│   ├── urls.py              # URL routing
│   └── wsgi.py              # WSGI configuration
├── model/                   # ML model files
│   ├── fake_news_lstm.h5    # Trained LSTM model
│   ├── tokenizer.pickle     # Text tokenizer
│   └── max_seq_len.txt      # Max sequence length
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎯 Usage

### User Registration
1. Navigate to `/signup/`
2. Enter username, email, and password
3. Click "Sign Up" to create account

### Login
1. Navigate to `/login/`
2. Enter email and password
3. Click "Login" to access the platform

### Detect Fake News
1. On the home page, enter text or URL
2. Click "Analyze" to get prediction
3. View results with confidence score

### Profile Management
1. Click on your username in the navbar
2. Edit email, first name, last name
3. Click "Save Changes" to update
4. Use "Change Password" to update password

### Admin Panel
1. Login with admin credentials
2. Access `/admin-panel/dashboard/`
3. Manage users, predictions, feedback, and settings

## 🔐 API Endpoints

### Public Endpoints
- `GET /` - Home page
- `GET /signup/` - User registration
- `POST /signup/` - Create new user
- `GET /login/` - Login page
- `POST /login/` - Authenticate user
- `POST /logout/` - Logout user

### User Endpoints (Authentication Required)
- `GET /profile/` - User profile page
- `POST /profile/` - Update user profile
- `GET /change-password/` - Change password page
- `POST /change-password/` - Update password
- `GET /predictions/` - List all predictions
- `GET /prediction/<id>/` - View prediction details
- `POST /feedback/<id>/` - Submit feedback
- `POST /vote/<id>/<type>/` - Vote on prediction

### Admin Endpoints (Admin Required)
- `GET /admin-panel/dashboard/` - Admin dashboard
- `GET /admin-panel/users/` - User management
- `POST /admin-panel/users/add/` - Add new admin
- `POST /admin-panel/users/<id>/delete/` - Delete user
- `POST /admin-panel/users/<id>/toggle-admin/` - Toggle admin status
- `GET /admin-panel/users/<id>/get/` - Get user details
- `POST /admin-panel/users/<id>/edit/` - Edit user
- `GET /admin-panel/activity/` - Activity logs
- `GET /admin-panel/feedback/` - Feedback management
- `POST /admin-panel/feedback/<id>/approve/` - Approve feedback
- `POST /admin-panel/feedback/<id>/reject/` - Reject feedback
- `GET /admin-panel/predictions/` - Prediction management
- `GET /admin-panel/predictions/export/` - Export predictions
- `GET /admin-panel/predictions/<id>/get/` - Get prediction details
- `POST /admin-panel/predictions/<id>/edit/` - Edit prediction
- `POST /admin-panel/predictions/<id>/delete/` - Delete prediction
- `GET /admin-panel/settings/` - System settings

## 🧠 Machine Learning Model

The fake news detection uses an LSTM (Long Short-Term Memory) neural network trained on news text data. The model processes text through a tokenizer, converts it to sequences, and predicts whether the content is "Real" or "Fake" with a confidence score.

### Model Features
- Text preprocessing and tokenization
- Sequence padding for uniform input length
- LSTM layers for sequential pattern recognition
- Confidence score calculation
- Real-time inference

## 📊 Database Models

### Prediction
- User who submitted the prediction
- Link URL (if applicable)
- Text content
- Prediction result (Real/Fake)
- Confidence score
- Approval status for retraining
- Creation timestamp

### Vote
- Associated prediction
- User who voted
- Vote type (Up/Down)
- Creation timestamp

### Feedback
- Associated prediction
- User who submitted feedback
- Corrected label
- Feedback notes
- Approval status
- Creation timestamp

### ActivityLog
- User who performed action
- Action type
- Action details
- Creation timestamp

## 🔒 Security Features

- User authentication with Django's built-in auth system
- CSRF protection for all forms
- Admin-only access to management features
- Password hashing and validation
- Session management
- SQL injection prevention (Django ORM)

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 📧 Contact

For questions or support, please contact the project maintainers.

## 🙏 Acknowledgments

- Django framework for the robust backend
- TensorFlow/Keras for machine learning capabilities
- Bootstrap for responsive UI design
- The open-source community for various libraries and tools

---

**Note**: This project is for educational purposes. Always verify information from multiple sources before making decisions based on fake news detection results.