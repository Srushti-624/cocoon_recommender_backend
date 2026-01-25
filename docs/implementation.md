# Backend API Implementation Plan

## Overview

This plan outlines the complete implementation of the **Cocoon Rearing Recommender System** backend API using FastAPI, MongoDB Atlas, and XGBoost ML models. The system will provide silk farmers with data-driven recommendations for optimal cocoon rearing schedules based on weather conditions, market prices, and ML predictions.

## User Review Required

> [!IMPORTANT]
> **ML Model Availability**: The implementation assumes XGBoost model files (`.pkl`) will be available in the `model/` directory. Please confirm:
> - Do you have trained model files ready?
> - What are the exact model file names?
> - What features does the model expect as input?

> [!IMPORTANT]
> **10-Day Graph Data**: The farmer dashboard should display a 10-day graph showing predicted prices and recommended dates. The implementation will generate predictions for the next 10 days from the current date, with the best start date highlighted. Please confirm this approach aligns with your requirements.

> [!WARNING]
> **Weather Data Source**: The project mentions fetching weather data based on location (Bengaluru, Ramanagar, Siddlaghatta). Should this be:
> - Fetched from an external weather API (e.g., OpenWeatherMap)?
> - Manually uploaded by admin users?
> - Pre-populated in the database?

---

## Proposed Changes

### Core Infrastructure

#### [NEW] [config.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/core/config.py)
- Environment configuration using Pydantic settings
- MongoDB connection string
- JWT secret key and algorithm
- CORS origins configuration
- Model file paths

#### [NEW] [security.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/core/security.py)
- Password hashing using bcrypt
- JWT token creation and verification
- Token expiration handling
- User authentication dependency

#### [NEW] [dependencies.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/core/dependencies.py)
- Current user dependency for protected routes
- Role-based access control (Farmer/Admin)
- Database session dependency

---

### Database Layer

#### [NEW] [mongo.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/database/mongo.py)
- MongoDB client initialization
- Database connection management
- Collection references (users, farmers, recommendations, market_weather)
- Connection lifecycle (startup/shutdown)

---

### Data Models

#### [NEW] [user_model.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/models/user_model.py)
- User schema with email, hashed password, role (Farmer/Admin)
- Pydantic models for request/response validation
- User registration and login DTOs

#### [NEW] [farmer_model.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/models/farmer_model.py)
- Farmer profile schema with user_id, district, experience, farming details
- Profile creation and update DTOs

#### [NEW] [recommendation_model.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/models/recommendation_model.py)
- Recommendation schema with user_id, city, start_date, end_date, predicted_price
- Prediction request and response DTOs
- Historical recommendation list model

#### [NEW] [market_weather_model.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/models/market_weather_model.py)
- Market and weather data schema
- Admin upload DTOs
- Data retrieval models

---

### Services Layer

#### [NEW] [ml_service.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/services/ml_service.py)
- Load XGBoost model and label encoders on startup
- Feature engineering and preprocessing
- Price prediction function
- Model health check

#### [NEW] [recommendation_service.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/services/recommendation_service.py)
- Orchestrate ML prediction and rule-based logic
- Generate 10-day prediction data for dashboard graph
- Identify best start date within 10-day window
- Calculate end date (rearing duration ~25-30 days)
- Save recommendations to database

#### [NEW] [rule_engine.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/services/rule_engine.py)
- Temperature-based rearing constraints (optimal: 20-28°C)
- Seasonal adjustments
- Date validation and adjustment logic
- Biologically safe rearing duration enforcement

#### [NEW] [weather_service.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/services/weather_service.py)
- Fetch current and forecasted weather data for cities
- Integration with weather API or database lookup
- Temperature data formatting for ML model

---

### Utilities

#### [NEW] [date_utils.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/utils/date_utils.py)
- Calculate rearing end date from start date
- Generate date ranges for 10-day predictions
- Season detection from date
- Date formatting utilities

---

### API Routes

#### [NEW] [auth_routes.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/routes/auth_routes.py)
**Endpoints:**
- `POST /api/auth/register` - User registration with email/password
- `POST /api/auth/login` - Authentication with JWT token response
- `GET /api/auth/me` - Get current user profile (protected)

**Features:**
- Email validation and uniqueness check
- Password hashing before storage
- JWT token generation with user_id and role
- Token-based authentication

#### [NEW] [farmer_routes.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/routes/farmer_routes.py)
**Endpoints:**
- `POST /api/farmer/profile` - Create or update farmer profile
- `GET /api/farmer/profile` - Retrieve farmer profile

**Features:**
- Farmer-only access control
- Profile upsert logic (create if not exists, update if exists)
- Link profile to authenticated user

#### [NEW] [admin_routes.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/routes/admin_routes.py)
**Endpoints:**
- `POST /api/admin/market-weather` - Upload market price and weather data
- `GET /api/admin/market-weather` - Retrieve stored data with filters

**Features:**
- Admin-only access control
- Bulk data upload support
- Date-based filtering
- City-based filtering

#### [NEW] [recommendation_routes.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/routes/recommendation_routes.py)
**Endpoints:**
- `POST /api/recommendation/predict` - Generate cocoon rearing recommendation
- `GET /api/recommendation/history` - Get user's recommendation history

**Features:**
- Accept city input from farmer
- Fetch weather data based on location
- Generate ML prediction
- Apply rule-based adjustments
- Calculate best start date within 10 days
- Save recommendation to database
- Return start date, end date, and predicted price

#### [NEW] [dashboard_routes.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/routes/dashboard_routes.py)
**Endpoints:**
- `GET /api/dashboard/farmer` - Farmer dashboard with 10-day graph data
- `GET /api/dashboard/admin` - Admin statistics and insights

**Farmer Dashboard Features:**
- Latest recommendation summary
- 10-day prediction graph data (dates, prices, end dates)
- Highlight best start date
- Recent recommendation history

**Admin Dashboard Features:**
- Total registered users (farmers/admins)
- Total recommendations generated
- Recent data upload status
- System health metrics

#### [NEW] [health_routes.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/routes/health_routes.py)
**Endpoints:**
- `GET /api/health` - System health check

**Features:**
- Database connection status
- ML model loading status
- API server status
- Timestamp of last check

---

### Main Application

#### [MODIFY] [main.py](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/src/main.py)
- Initialize FastAPI application
- Configure CORS middleware
- Register all route modules
- Database connection lifecycle events
- ML model loading on startup
- Global exception handlers
- API documentation configuration

---

### Environment Configuration

#### [MODIFY] [.env](file:///c:/Users/HP/Desktop/Capstone/Project/Backend/.env)
- MongoDB connection URI
- JWT secret key
- JWT algorithm and expiration
- CORS allowed origins
- Model file paths
- Weather API key (if applicable)

---

## Verification Plan

### Automated Tests

1. **Authentication Flow**
   ```bash
   # Test user registration
   curl -X POST http://localhost:8000/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"email":"farmer@test.com","password":"test123","role":"Farmer"}'
   
   # Test login
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"farmer@test.com","password":"test123"}'
   ```

2. **Farmer Profile Management**
   ```bash
   # Create farmer profile (with JWT token)
   curl -X POST http://localhost:8000/api/farmer/profile \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"district":"Bengaluru","experience":5}'
   ```

3. **Recommendation Generation**
   ```bash
   # Generate recommendation
   curl -X POST http://localhost:8000/api/recommendation/predict \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"city":"Bengaluru"}'
   ```

4. **Dashboard Data**
   ```bash
   # Get farmer dashboard
   curl -X GET http://localhost:8000/api/dashboard/farmer \
     -H "Authorization: Bearer <token>"
   ```

5. **Health Check**
   ```bash
   # Verify system health
   curl -X GET http://localhost:8000/api/health
   ```

### Manual Verification

1. **Database Inspection**
   - Verify user documents are created with hashed passwords
   - Check recommendation documents contain all required fields
   - Validate market/weather data storage

2. **ML Model Integration**
   - Confirm model loads successfully on startup
   - Verify predictions are reasonable values
   - Test with different city inputs

3. **10-Day Graph Data**
   - Verify dashboard returns 10 data points
   - Confirm best start date is within 10-day window
   - Check date calculations are correct

4. **Role-Based Access**
   - Test farmer cannot access admin endpoints
   - Test admin cannot access farmer-specific endpoints
   - Verify JWT token validation

5. **API Documentation**
   - Access Swagger UI at `http://localhost:8000/docs`
   - Test all endpoints through interactive documentation
   - Verify request/response schemas

---

## Implementation Notes

### Key Design Decisions

1. **Hybrid ML + Rule-Based Approach**: ML model provides price predictions, while rule-based logic ensures practical constraints (temperature limits, seasonal factors, biological requirements)

2. **10-Day Prediction Window**: System generates predictions for next 10 days and identifies the optimal start date within this window, providing farmers with actionable short-term planning

3. **Automatic Weather Fetching**: Based on city selection, system automatically fetches weather data rather than requiring manual input from farmers

4. **Recommendation History**: All predictions are saved to database for historical analysis and farmer reference

5. **Role-Based Security**: JWT-based authentication with role enforcement ensures farmers and admins have appropriate access levels

### Technical Considerations

- **Model Loading**: ML models loaded once at startup for performance efficiency
- **Date Calculations**: Rearing duration assumed to be 25-30 days based on sericulture best practices
- **Temperature Constraints**: Optimal range 20-28°C; recommendations adjusted if outside this range
- **City Support**: Initially supporting Bengaluru, Ramanagar, and Siddlaghatta as specified
- **MongoDB Indexes**: Consider adding indexes on user_id, city, and date fields for query performance

---

**End of Implementation Plan**


