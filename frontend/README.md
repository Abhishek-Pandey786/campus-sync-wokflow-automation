# Workflow Automation — React Frontend

Built with **Vite + React 18 + Tailwind CSS**.

## Prerequisites

- Node.js 18+ installed
- Backend running at `http://localhost:8000`

## Setup & Run

```bash
# Install dependencies
npm install

# Start development server (http://localhost:5173)
npm run dev

# Build for production
npm run build
```

## Pages

| Page           | Route          | Description                                              |
| -------------- | -------------- | -------------------------------------------------------- |
| Login          | `/login`       | JWT authentication                                       |
| Dashboard      | `/`            | Stats overview + model status                            |
| Requests       | `/requests`    | Browse 1,200+ service requests; click row for timeline   |
| ML Predictions | `/predictions` | Real-time delay prediction form                          |
| Analytics      | `/analytics`   | Charts: delay rates, type breakdown, status distribution |
| Alerts         | `/alerts`      | High-risk requests with SLA countdown + admin escalation |

## Stack

- **Vite** — fast dev server + build tool
- **React 18** — UI framework
- **React Router v6** — client-side routing
- **Tailwind CSS** — utility-first styling
- **Axios** — HTTP client with JWT interceptor
- **Recharts** — React-native charting library

## Demo Credentials

```
Email:    admin@university.edu
Password: Admin@123
```
