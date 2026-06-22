import { Navigate, Route, Routes } from "react-router-dom";
import { DemoLayout } from "./components/DemoLayout";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import MobileApp from "./pages/MobileApp";
import WebApp from "./pages/WebApp";
import Training from "./pages/Training";

export default function App() {
  return (
    <Routes>
      <Route element={<DemoLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/mobile" element={<MobileApp />} />
        <Route path="/web" element={<WebApp />} />
        <Route path="/training" element={<Training />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
