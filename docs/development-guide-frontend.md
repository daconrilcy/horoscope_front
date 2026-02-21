# Development Guide - Frontend

## Prerequisites
- Node.js (current LTS recommended)
- npm

## Setup
```powershell
cd frontend
npm ci
```

## Run
```powershell
cd frontend
npm run dev
```

## Build
```powershell
cd frontend
npm run build
```

## Quality and Tests
```powershell
cd frontend
npm run lint
npm run test
npm run test:b2b
```

## Front/Back Integration
- Backend expected locally on `http://localhost:8000`
- Frontend dev server default `http://localhost:5173`
- API domain clients are centralized in `frontend/src/api/`
