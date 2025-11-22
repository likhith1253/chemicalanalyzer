# 🔐 Session-Based Login Implemented

## What Changed?
I have updated the application to use **Session Storage** instead of **Local Storage** for storing your login session.

## What This Means
- **Before**: You stayed logged in even after closing the browser (Persistent).
- **Now**: You will be **automatically logged out** when you close the browser tab or window.
- **Reloading**: Refreshing the page (F5) will **keep you logged in**.

## How to Test
1. **Login** to the application.
2. **Refresh** the page -> You should stay logged in.
3. **Close** the browser tab.
4. **Open** a new tab and go to `http://localhost:5173`.
5. **Result**: You should be asked to **Login** again.

## Technical Details
- Modified `src/api/client.js` to use `sessionStorage`.
- Modified `src/pages/DashboardPage.jsx` to check `sessionStorage`.
- Modified `src/contexts/AuthContext.jsx` (indirectly via client.js helpers).
