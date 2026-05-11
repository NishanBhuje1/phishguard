import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Scanner from './pages/Scanner'
import AdminDashboard from './pages/AdminDashboard'

const PrivateRoute = ({ children }) =>
  localStorage.getItem('token') ? children : <Navigate to="/" />

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/scanner" element={<PrivateRoute><Scanner /></PrivateRoute>} />
        <Route path="/admin" element={<PrivateRoute><AdminDashboard /></PrivateRoute>} />
      </Routes>
    </BrowserRouter>
  )
}
