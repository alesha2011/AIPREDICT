import { Routes, Route, Navigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { Dashboard } from './pages/Dashboard';
import { Register } from './pages/Register';
import { Login } from './pages/Login';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const token = Cookies.get('auth_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>

      {/* Абстрактные фоновые элементы */}
      <div
        className="fixed top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full pointer-events-none z-[-1]"
        style={{ background: 'rgba(0, 240, 255, 0.05)', filter: 'blur(120px)' }}
      />
      <div
        className="fixed bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full pointer-events-none z-[-1]"
        style={{ background: 'rgba(0, 51, 255, 0.10)', filter: 'blur(150px)' }}
      />
    </>
  );
}

export default App;
