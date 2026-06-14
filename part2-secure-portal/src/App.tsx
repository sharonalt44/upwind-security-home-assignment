import { Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import SignInPage from "./components/SignInPage";
import ProtectedRoute from "./components/ProtectedRoute";
import WelcomeBanner from "./components/WelcomeBanner";
import EventsPage from "./pages/EventsPage";
import UsersPage from "./pages/UsersPage";
import NotFound from "./pages/NotFound";

function AppContent() {
  const { user, loading, setUser } = useAuth();

  if (loading) {
    return (
      <div className="sign-in-page">
        <p>Checking session…</p>
      </div>
    );
  }

  if (!user) {
    return <SignInPage onSuccess={setUser} />;
  }

  return (
    <>
      <Navbar />
      <div className="container">
        <WelcomeBanner />
        <Routes>
          <Route path="/" element={<Navigate to="/events" replace />} />
          <Route
            path="/events"
            element={
              <ProtectedRoute>
                <EventsPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/users"
            element={
              <ProtectedRoute adminOnly>
                <UsersPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
