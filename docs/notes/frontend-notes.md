# Frontend Development Experience

Building the frontend for ChemViz was an exciting journey into modern React development. I wanted to create something that looked professional and felt smooth to use, so I dove deep into component architecture and modern UI patterns.

## Tech Stack Choices

I went with **React 18** and **Vite** as the build tool. Vite is incredibly fast compared to traditional webpack setups - the hot module replacement during development is almost instant. For routing, I used **React Router v6** which has a much cleaner API than the older versions.

For charts and visualizations, I integrated two libraries:
- **Chart.js** with **react-chartjs-2** for the main dashboard charts
- **Recharts** for some specialized visualizations

I also added **Lucide React** for beautiful, consistent icons throughout the app.

## Project Structure

I organized everything in a clean, modular way:

```
web-frontend/
├── src/
│   ├── api/              # API communication layer
│   │   └── client.js     # Centralized axios instance
│   ├── components/       # Reusable UI components
│   │   ├── DatasetCard.jsx
│   │   ├── Navigation.jsx
│   │   ├── SummaryCards.jsx
│   │   └── *.css files
│   ├── pages/            # Route pages
│   │   ├── Home.jsx
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   ├── Upload.jsx
│   │   ├── Dashboard.jsx
│   │   └── DatasetDetail.jsx
│   ├── config.js         # Environment configuration
│   ├── App.jsx          # Main app component
│   └── main.jsx         # Entry point
```

## API Integration

One of the most important pieces was setting up a solid API client. I created a centralized axios instance in `api/client.js` that:

- Automatically includes auth tokens in requests
- Has a base URL that switches between dev and production
- Handles token refresh and logout on 401 errors
- Provides clean error messages

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
```

This environment variable approach made deployment super smooth - I just set `VITE_API_BASE_URL` in Vercel and everything worked.

## Component Design

I built several key components:

### Navigation Component
A responsive navbar that shows different options when logged in vs logged out. It handles the active link highlighting and mobile menu collapse.

### SummaryCards
These display the key metrics on the dashboard - total datasets, average flowrate, equipment count, etc. I used glassmorphism effects to make them look modern and clean.

### DatasetCard
Each uploaded dataset gets its own card showing preview info. I added hover effects and smooth transitions to make the UI feel alive.

### Charts Integration
Getting Chart.js working with React was interesting. I had to learn about refs and how to properly configure the responsive behavior. The key was creating proper config objects with all the Chart.js options.

## Routing & Protected Routes

I set up React Router with both public and protected routes. The authentication check happens in the route definitions - if you're not logged in, you automatically get redirected to the login page.

## State Management

I kept it simple and didn't use Redux or other state libraries. Instead, I used:
- React's `useState` and `useEffect` hooks for component state
- localStorage for persisting auth tokens
- Context for sharing auth state (when needed)

This kept the bundle size small and the code easy to understand.

## Styling Approach

I went with vanilla CSS rather than Tailwind or CSS-in-JS. This gave me complete control over the design. My key patterns:

- **CSS Variables** for colors and spacing
- **Flexbox and Grid** for layouts
- **Glassmorphism** effects with backdrop-filter
- **Smooth animations** on hover and load
- **Mobile-first responsive design**

The glassmorphism was achieved with:
```css
background: rgba(255, 255, 255, 0.1);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.2);
```

## User Experience Details

I added several UX improvements:

- **Toast notifications** using react-hot-toast for all user actions
- **Loading states** on buttons and data fetches
- **Error handling** with friendly messages
- **Empty states** when there's no data yet
- **Smooth page transitions**

## Environment Configuration

The `config.js` file centralizes all environment-dependent settings:

```javascript
const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  environment: import.meta.env.VITE_ENVIRONMENT || 'development',
};
```

This made it easy to switch between local development and production without changing code.

## Build & Deployment

Deployment to Vercel was incredibly straightforward:

1. Connected my GitHub repo
2. Set root directory to `web-frontend`
3. Vercel auto-detected Vite settings
4. Added `VITE_API_BASE_URL` environment variable
5. Hit deploy!

The build command (`npm run build`) creates an optimized production bundle in the `dist` folder. Vercel's CDN serves it globally with excellent performance.

## Challenges & Solutions

**CORS Issues**: Initially had CORS errors connecting to the backend. Fixed by ensuring the backend had the correct `CORS_ALLOWED_ORIGINS` setting.

**Token Management**: Had to figure out where to store auth tokens. Went with localStorage as it persists across sessions and is simple to use.

**Chart Responsiveness**: Charts weren't resizing properly at first. Fixed by setting `maintainAspectRatio: false` and using a container div with defined dimensions.

**File Uploads**: File upload with FormData was tricky. Had to ensure the `Content-Type` header was NOT set manually - browser handles it automatically for multipart/form-data.

## Performance Optimizations

- **Code splitting** with React.lazy() for route-based splitting
- **Memoization** with useMemo and useCallback where appropriate
- **Debouncing** on search inputs
- **Optimized images** and assets
- **Tree shaking** via Vite's build process

## Development Workflow

My typical dev workflow:

1. Run `npm run dev` - instant startup
2. Make changes - see them live immediately
3. Test in browser dev tools
4. Commit and push to GitHub
5. Vercel auto-deploys from main branch

The hot reload in Vite is so fast that I barely notice it - the page updates almost as I type.

## Final Thoughts

Building this frontend taught me a lot about modern React patterns and production deployment. The combination of React, Vite, and Vercel creates an incredibly smooth development and deployment experience. The end result is a fast, responsive, and beautiful web app that I'm proud to show off.

The live site is running at: https://chemicalanalyzer.vercel.app
