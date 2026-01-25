# Project Documentation

## Title

**A Recommender System to Benefit Silk Farmers for Preparing a Short-Term Schedule of Cocoon Rearing**

---

## 1. Introduction

Sericulture (silk farming) plays a crucial role in supporting rural livelihoods in India, especially in states like Karnataka. However, silk farmers face continuous challenges due to fluctuating market prices, unpredictable weather conditions, and the biological sensitivity of silkworm rearing. Decisions such as *when to start a cocoon rearing cycle* significantly impact yield quality and farmer income.

This project proposes a **machine learning–based recommender system** that assists silk farmers in planning **short-term cocoon rearing schedules**. The system predicts expected cocoon prices and recommends the optimal start and end dates for rearing by integrating market data, temperature conditions, seasonal factors, and rule-based agricultural logic.

---

## 2. What Is This Project About?

This project is a **full-stack intelligent decision-support system** that provides actionable recommendations to silk farmers. It uses historical and current data to predict outcomes and guide farmers toward better planning decisions.

The system:

* Accepts **weather and market inputs** from the farmer or admin
* Applies **trained machine learning models** to predict expected cocoon prices
* Uses **rule-based logic** to adjust predictions according to environmental constraints
* Generates a **short-term cocoon rearing schedule**
* Stores recommendations for future reference

The final output is a **clear, farmer-friendly recommendation** that answers:

* When should I start cocoon rearing?
* When is the expected harvesting/end date?
* What price can I expect in the market at end date/harvesting date?

---

## 3. Who Needs This Project?

### Primary Users

* **Silk Farmers**: To plan cocoon rearing cycles more scientifically instead of relying only on traditional experience or delayed market information.

### Secondary Users

* **Agricultural Administrators / Market Committees**: To upload market and weather data and analyze farmer trends.
* **Researchers & Academicians**: To study the impact of AI-based recommendations in sericulture.

---

## 4. Why Are We Building This Project?

Silk farmers currently face several limitations:

* Lack of real-time or predictive market insights
* High dependency on traditional knowledge
* Risk of loss due to wrong timing decisions
* No integrated platform combining market, weather.

This project is built to:

* Reduce uncertainty in cocoon rearing decisions
* Improve farmer income and productivity
* Introduce data-driven planning into sericulture
* Bridge the gap between research models and real-world farmer applications

---

## 5. System Overview

The system follows a **client–server architecture** with machine learning integration:

* **Frontend (React)**: User interface for farmers and admins
* **Backend (FastAPI)**: Business logic, ML inference, authentication
* **Machine Learning Models**: Predict cocoon prices and assist scheduling
* **Database (MongoDB Atlas)**: Stores users, inputs, and recommendations

---

## 6. Input to the System

### Farmer Inputs

* City / District(Bengaluru, Ramanagar,Siddlaghatta) we are using these 3 cities only.
farmer input is just the location , based on the loaction the system will fetch the weather data and market data.

### Admin Inputs

* Daily market prices
* Weather/temperature data
* Dataset updates (if required)

All inputs are validated and sent to the backend in JSON format.

---

## 7. Machine Learning Component

The backend integrates **multiple trained ML models** stored in `.pkl` format:

* **XGBoost model** for cocoon price prediction
* **Label encoders** for categorical features like city and season

### ML Workflow

1. Input data is received from the frontend
2. Categorical values are encoded using saved encoders
3. Numerical features are formatted
4. The trained model predicts the expected cocoon price

The ML model focuses on *prediction accuracy*, while decision logic is handled separately.

---

## 8. Rule-Based Recommendation Logic

To ensure realistic and farmer-friendly recommendations, **rule-based logic** is applied on top of ML predictions. Examples include:

* Delaying rearing start if temperature exceeds safe limits
* Adjusting schedules based on seasonal constraints
* Ensuring biologically safe rearing durations

This hybrid approach ensures both **accuracy and practicality**.

---

## 9. Output of the System

The system generates the following outputs:

* **Best start date** for cocoon rearing(the best start date recommendation should be within 10 days from the current date)  
And even i need a graph for the best start date recommendation.(and 10 days graph should be displayed on the dashboard from the current date including the best start date with expected price and end date also)
* **Expected end/harvesting date**
* **Predicted cocoon market price at the end date/harvesting date**
s
These results are:

* Displayed on the farmer dashboard
* Stored in MongoDB for future reference
* Used for historical analysis and reporting

---

## 10. Authentication and Security

The system uses:

* Email and password–based registration
* Secure password hashing
* JWT (JSON Web Token) authentication
* Role-based access (Farmer / Admin)

This ensures data privacy and secure access to recommendations.

---

## 11. Data Storage

MongoDB Atlas is used to store:

* User authentication data
* Farmer profiles
* Market and weather data
* Generated recommendations and history

The document-oriented structure allows flexibility and scalability.

---

## 12. Deployment Strategy

* **Frontend**: Deployed on Render
* **Backend**: Deployed on Render with FastAPI
* **Database**: MongoDB Atlas (cloud-based)

This setup ensures accessibility, scalability, and real-world usability.

---

## 13. Expected Impact

* Improved decision-making for silk farmers
* Reduced financial risk
* Increased cocoon yield quality
* Promotion of AI adoption in agriculture
* Support for sustainable sericulture practices

---

## 14. Conclusion

This project demonstrates how machine learning, when combined with domain-specific rules and a user-friendly platform, can solve real-world agricultural problems. The **Cocoon Rearing Recommender System** provides a practical, scalable, and impactful solution that empowers silk farmers with data-driven insights, ultimately contributing to economic stability and sustainable farming practices.

---

**End of Document**
