// src/App.tsx
import React, { useEffect } from 'react';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
  useLocation,
} from 'react-router-dom';
import Cookies from 'js-cookie';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import NotFoundPage from './pages/NotFoundPage';

const AutoRedirect = () => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const token = Cookies.get('token');
    // 只有在访问登录或注册页面时，如果检测到 token，则重定向到 dashboard
    if (token && (location.pathname === '/login' || location.pathname === '/register')) {
      navigate('/dashboard');
    }
  }, [navigate, location.pathname]);

  return null;
};

const ProtectedRoute = ({ children }) => {
  const location = useLocation();
  const token = Cookies.get('token');

  if (!token) {
    // 如果没有 token，则重定向到登录页面，并传递当前尝试访问的页面路径作为参数（可选）
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

function App() {
  return (
    <Router>
      <AutoRedirect />
      <Routes>
        {/* 根路径自动重定向到登录页 */}
        <Route path="/" element={<Navigate replace to="/login" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" 
               element={
                  <ProtectedRoute>
                    <DashboardPage />
                  </ProtectedRoute>
                }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  );
}

export default App;