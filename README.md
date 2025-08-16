# Invoice Automation Application

A full-stack web application for automated invoice management with integrated payment processing via Stripe and PayPal.

## 🚀 Features

- **User Authentication**: Secure JWT-based authentication system
- **Invoice Management**: Create, edit, and manage professional invoices
- **Client Management**: Organize customer information and billing details
- **Payment Processing**: Integrated Stripe and PayPal payment gateways
- **PDF Generation**: Automatic invoice PDF generation
- **Email Notifications**: Send invoices directly to clients
- **Analytics Dashboard**: Business insights and reporting
- **Multi-currency Support**: Handle different currencies and tax rates
- **Responsive Design**: Modern UI that works on all devices

## 🏗️ Architecture

### Backend (Flask + Python)
- **Framework**: Flask 2.3.3 with RESTful API
- **Database**: MongoDB with MongoEngine ODM
- **Authentication**: JWT tokens with refresh mechanism
- **Payment**: Stripe and PayPal integration
- **Background Tasks**: Celery with Redis
- **PDF Generation**: ReportLab for invoice PDFs
- **Email**: SMTP/SendGrid integration

### Frontend (Nuxt.js + Vue.js)
- **Framework**: Nuxt.js 3 with Vue.js 3
- **Styling**: Tailwind CSS with custom design system
- **State Management**: Pinia store
- **UI Components**: Headless UI + Heroicons
- **Charts**: Chart.js for analytics
- **Forms**: VeeValidate with Yup validation

## 📋 Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.9+
- **MongoDB** 6.0+
- **Redis** 6.0+
- **Docker** and Docker Compose (optional)

## 🛠️ Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd create-bill-automatique
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - MongoDB: localhost:27017
   - Redis: localhost:6379

### Option 2: Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Start MongoDB and Redis**
   ```bash
   # Start MongoDB (install MongoDB first)
   mongod
   
   # Start Redis (install Redis first)
   redis-server
   ```

6. **Run the backend**
   ```bash
   python app.py
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   # Create .env file with your API configuration
   echo "NUXT_PUBLIC_API_BASE_URL=http://localhost:5000/api" > .env
   ```

4. **Run the frontend**
   ```bash
   npm run dev
   ```

## ⚙️ Configuration

### Environment Variables

#### Backend (.env)
```env
# Database
MONGODB_URI=mongodb://localhost:27017/invoice_app
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET_KEY=your-secret-jwt-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000

# Stripe
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# PayPal
PAYPAL_CLIENT_ID=your_client_id
PAYPAL_CLIENT_SECRET=your_client_secret
PAYPAL_ENVIRONMENT=sandbox

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email
MAIL_PASSWORD=your_app_password
```

#### Frontend (.env)
```env
NUXT_PUBLIC_API_BASE_URL=http://localhost:5000/api
NUXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_test_...
NUXT_PUBLIC_PAYPAL_CLIENT_ID=your_client_id
```

## 🚀 Usage

### 1. First Time Setup

1. **Register a new account** at http://localhost:3000/register
2. **Complete your company profile** with business information
3. **Configure payment gateways** in Settings > Payments

### 2. Managing Clients

1. Navigate to **Clients** section
2. **Add new clients** with complete billing information
3. **Organize clients** with tags and notes

### 3. Creating Invoices

1. Go to **Invoices** > **New Invoice**
2. **Select a client** from your client list
3. **Add invoice items** with descriptions, quantities, and prices
4. **Set tax rates** and additional fees
5. **Preview and send** the invoice

### 4. Payment Processing

1. **Configure Stripe/PayPal** in your account settings
2. **Send invoices** to clients via email
3. **Monitor payments** in real-time through webhooks
4. **Track payment status** in the dashboard

### 5. Reports and Analytics

1. **View dashboard** for business overview
2. **Generate reports** for revenue, clients, and invoices
3. **Export data** in various formats
4. **Track performance** over time

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Invoices
- `GET /api/invoices` - List invoices
- `POST /api/invoices` - Create invoice
- `GET /api/invoices/{id}` - Get invoice details
- `PUT /api/invoices/{id}` - Update invoice
- `DELETE /api/invoices/{id}` - Delete invoice
- `POST /api/invoices/{id}/send` - Send invoice

### Clients
- `GET /api/clients` - List clients
- `POST /api/clients` - Create client
- `GET /api/clients/{id}` - Get client details
- `PUT /api/clients/{id}` - Update client
- `DELETE /api/clients/{id}` - Delete client

### Payments
- `POST /api/payments/stripe/create-intent` - Create Stripe payment
- `POST /api/payments/paypal/create-order` - Create PayPal order
- `POST /api/payments/stripe/webhook` - Stripe webhook
- `POST /api/payments/paypal/webhook` - PayPal webhook

### Reports
- `GET /api/reports/dashboard` - Dashboard data
- `GET /api/reports/revenue` - Revenue reports
- `GET /api/reports/clients` - Client performance
- `POST /api/reports/export` - Export data

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm run test
```

### E2E Tests
```bash
cd frontend
npm run test:e2e
```

## 📦 Deployment

### Production Deployment

1. **Update environment variables** for production
2. **Use production database** (MongoDB Atlas, etc.)
3. **Configure SSL certificates** for HTTPS
4. **Set up monitoring** and logging
5. **Use production payment keys** for Stripe/PayPal

### Docker Production
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Features

- **JWT Authentication** with refresh tokens
- **Password hashing** with Werkzeug
- **CORS protection** for API endpoints
- **Input validation** and sanitization
- **Rate limiting** (can be added)
- **HTTPS enforcement** in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the code comments and API documentation
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Use GitHub Discussions for questions and help

## 🙏 Acknowledgments

- **Vue.js** and **Nuxt.js** for the amazing frontend framework
- **Flask** for the robust Python web framework
- **MongoDB** for the flexible NoSQL database
- **Stripe** and **PayPal** for payment processing
- **Tailwind CSS** for the utility-first CSS framework

---

**Happy invoicing! 🎉**