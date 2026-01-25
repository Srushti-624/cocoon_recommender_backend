# Cocoon Rearing Recommender - Frontend Specification

## Project Overview

Build a modern, aesthetically pleasing React.js frontend for the **Cocoon Rearing Recommender System**. This application helps silk farmers in Karnataka, India determine the optimal time to start cocoon rearing based on ML-powered market price predictions and real-time weather data.

---

## Design Requirements

### Color Palette (Pastel Theme)
Use a soft, calming pastel color scheme:

| Usage | Color | Hex |
|-------|-------|-----|
| Primary | Soft Lavender | `#E6E6FA` |
| Secondary | Mint Green | `#98FB98` |
| Accent | Peach | `#FFDAB9` |
| Background | Cream White | `#FFFAF0` |
| Card Background | Soft White | `#FFFFFF` |
| Text Primary | Dark Slate | `#2F4F4F` |
| Text Secondary | Gray | `#696969` |
| Success | Soft Green | `#90EE90` |
| Warning | Soft Yellow | `#FFFACD` |
| Error | Soft Coral | `#F08080` |
| Chart Line | Soft Blue | `#87CEEB` |
| Best Date Highlight | Soft Gold | `#FFD700` |

### Typography
- Headings: `Poppins` or `Nunito` (rounded, friendly)
- Body: `Inter` or `Open Sans`
- Numbers/Data: `Roboto Mono` for prices

### UI Style
- Soft shadows and rounded corners (16px border-radius)
- Glassmorphism effects where appropriate
- Smooth transitions and micro-animations
- Card-based layout with generous spacing
- Mobile-first responsive design

---

## Pages & Components

### 1. Landing Page (`/`)
- Hero section with app name and tagline
- Brief explanation of what the app does
- "Get Started" button → Login/Register
- Illustration of silkworm/cocoon farming (optional)

### 2. Authentication Pages

#### Login Page (`/login`)
- Email and password fields
- "Login" button
- Link to register page
- Soft gradient background

#### Register Page (`/register`)
- Email, password, confirm password
- Name (optional)
- Role selection: **Farmer** or **Admin** (radio buttons or toggle)
- "Create Account" button
- Link to login page

**API Integration:**
- `POST /api/auth/register`
- `POST /api/auth/login`
- Store JWT token in localStorage or secure cookie

### 3. Farmer Dashboard (`/dashboard`) - Overview Page
This is the **home page** after login. It shows a summary of useful information and past activity.
**This page uses history data to display insights.**

#### Components:

##### A. Welcome Header
- Greeting with user name: "Welcome back, [Name]!"
- Current date and time
- Quick stats row (cards):
  - **Total Predictions Made** (count from history)
  - **Last Prediction Date**
  - **Average Predicted Price** (calculated from history)

##### B. Recent Recommendations Card
Display the **last 3-5 recommendations** from history in a visually appealing card layout.
Each card shows:
- City name with icon
- Predicted price (₹)
- Start date → End date
- When it was created (e.g., "2 days ago")

##### C. Price Trend Mini Chart (Optional)
If the user has 5+ historical predictions, show a small line chart of their past predicted prices over time.

##### D. Quick Action Card
- "Generate New Prediction" button → navigates to `/predict` page
- Brief text: "Get today's recommendation based on real-time weather"

##### E. Navigation Sidebar/Menu
- Dashboard (current)
- New Prediction
- Profile
- Logout

**API Used on Dashboard:**
- `GET /api/recommendation/history` - to populate all dashboard data
- `GET /api/auth/me` - to get user name

---

### 4. Predict Page (`/predict`) - Generate New Predictions
This is a **separate page** where farmers generate new predictions.

#### Components:

##### A. City Selection Card
- Large, prominent card with city options:
  - Bengaluru
  - Ramanagar
  - Siddlaghatta
- Use radio buttons, toggle pills, or clickable cards with city icons
- **"Generate Prediction"** button (prominent, pastel green, with icon)

##### B. Current Prediction Result Card
After generating a prediction, display:
- **Recommended Start Date** (large, highlighted with calendar icon)
- **Expected End Date**
- **Predicted Market Price** (in ₹, large font, emphasized)
- **Rearing Duration** (e.g., "28 days")
- **Current Weather Conditions Box**:
  - 🌡️ Temperature (avg & max)
  - 💧 Humidity
  - 🌧️ Rainfall
- Confidence indicator (progress bar or percentage badge)

##### C. 10-Day Prediction Chart ⭐ CRITICAL
**This chart MUST be displayed every time a prediction is generated.**
It helps farmers choose the best day to start within a 10-day window.

- **Chart Type**: Line chart (preferred) or bar chart
- **X-Axis**: Dates (next 10 days)
- **Y-Axis**: Predicted Price (₹)
- **Features**:
  - Highlight the **best date** with a different color (gold/yellow star marker)
  - Show tooltip on hover with exact price, temperature, and date
  - Animate the chart on load (line drawing animation)
  - Display a prominent label/badge: "🌟 Best Day to Start: Jan 31"
  - Show price on Y-axis with ₹ symbol

**Recommended Libraries:**
- `recharts` (simple, React-friendly) ✅ Recommended
- `chart.js` with `react-chartjs-2`
- `visx` (for custom visualizations)

**API Integration on Predict Page:**
When user clicks "Generate Prediction":
1. Call `POST /api/recommendation/predict` with `{ "city": "Bengaluru" }`
2. **Immediately** call `GET /api/recommendation/10day-graph?city=Bengaluru`
3. Display both results together on the same page
4. Show loading spinner while fetching

##### D. "Save & View History" Button
After prediction is shown, offer button to go back to Dashboard to see updated history.

---

### 5. Farmer Profile Page (`/profile`)
- Display current profile info
- Form to update:
  - District
  - Experience (years)
  - Farm size (acres)
  - Phone number
- Save button

**API:**
- `GET /api/farmer/profile`
- `POST /api/farmer/profile`

### 6. Admin Dashboard (`/admin`) - Admin Only
- Total users count
- Total predictions generated
- Form to upload market/weather data
- Table of uploaded data with filters

**API:**
- `POST /api/admin/market-weather`
- `GET /api/admin/market-weather`

---

## User Flow

```
┌─────────────────┐
│  Landing Page   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Login/Register │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│                  FARMER DASHBOARD                         │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Welcome back, John!              Jan 25, 2026     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                │
│  │ Total    │  │ Last     │  │ Avg      │                │
│  │ Preds: 12│  │ Jan 25   │  │ ₹485     │                │
│  └──────────┘  └──────────┘  └──────────┘                │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         RECENT RECOMMENDATIONS                      │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐               │  │
│  │  │Bengaluru│ │Ramanagar│ │Siddla.. │               │  │
│  │  │ ₹521    │ │ ₹485    │ │ ₹499    │               │  │
│  │  │ Jan 31  │ │ Jan 28  │ │ Jan 25  │               │  │
│  │  └─────────┘ └─────────┘ └─────────┘               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  🌟 Generate New Prediction                    →   │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                         │
                         │ Click "New Prediction"
                         ▼
┌──────────────────────────────────────────────────────────┐
│                    PREDICT PAGE                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Select City:                                       │  │
│  │  [Bengaluru]  [Ramanagar]  [Siddlaghatta]          │  │
│  │                                                     │  │
│  │         [ 🔮 Generate Prediction ]                  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  YOUR PREDICTION                                    │  │
│  │  Start: Jan 31  →  End: Feb 28                     │  │
│  │  Predicted Price: ₹521.06                          │  │
│  │  Weather: 21°C | 68% humidity | 0mm rain           │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │        10-DAY PREDICTION CHART                      │  │
│  │  ₹ │          ★ Best Day                           │  │
│  │  520│         /\                                    │  │
│  │  500│   /\   /  \                                   │  │
│  │  480│  /  \_/    \___                               │  │
│  │  460│ /                                             │  │
│  │     └──────────────────────────                     │  │
│  │      Jan 25  27  29  31  Feb 2  4                   │  │
│  │                                                     │  │
│  │  🌟 Best day to start: January 31 (₹521)           │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## API Integration Summary

| Action | Method | Endpoint | Auth Required |
|--------|--------|----------|---------------|
| Register | POST | `/api/auth/register` | No |
| Login | POST | `/api/auth/login` | No |
| Get Current User | GET | `/api/auth/me` | Yes |
| Get Farmer Profile | GET | `/api/farmer/profile` | Farmer |
| Update Profile | POST | `/api/farmer/profile` | Farmer |
| Generate Prediction | POST | `/api/recommendation/predict` | Farmer |
| Get 10-Day Graph | GET | `/api/recommendation/10day-graph?city=X` | Farmer |
| Get History | GET | `/api/recommendation/history` | Farmer |
| Upload Data | POST | `/api/admin/market-weather` | Admin |
| Get Data | GET | `/api/admin/market-weather` | Admin |
| Health Check | GET | `/api/health` | No |

**Base URL:** `http://localhost:8000`

---

## Key Features Checklist

- [ ] JWT Authentication with protected routes
- [ ] Role-based access (Farmer vs Admin views)
- [ ] City selection dropdown
- [ ] Single prediction display card
- [ ] **10-Day Prediction Line/Bar Chart** (REQUIRED)
  - [ ] Highlight best date
  - [ ] Tooltips on hover
  - [ ] Animated rendering
- [ ] Recommendation history list
- [ ] Profile management
- [ ] Responsive design (mobile + desktop)
- [ ] Loading states and error handling
- [ ] Pastel color theme throughout
- [ ] Smooth animations and transitions

---

## Sample Component: 10-Day Chart (Recharts)

```jsx
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceDot } from 'recharts';

const TenDayChart = ({ predictions, bestDate }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={predictions}>
        <XAxis dataKey="date" />
        <YAxis domain={['auto', 'auto']} />
        <Tooltip />
        <Line 
          type="monotone" 
          dataKey="predicted_price" 
          stroke="#87CEEB" 
          strokeWidth={3}
          dot={{ fill: '#E6E6FA', r: 6 }}
          activeDot={{ r: 8, fill: '#FFD700' }}
        />
        {/* Highlight best date */}
        <ReferenceDot 
          x={bestDate} 
          y={predictions.find(p => p.date === bestDate)?.predicted_price}
          r={10}
          fill="#FFD700"
          stroke="none"
        />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

---

## Notes for Development

1. **Always fetch both prediction AND 10-day graph together** when user generates a prediction
2. Use tanstack query for state management and api calls.
3. Add loading spinners during API calls
4. Show toast notifications for success/error messages
5. The app is for silk farmers in India - consider regional context in copy/messaging

---

**End of Frontend Specification**
