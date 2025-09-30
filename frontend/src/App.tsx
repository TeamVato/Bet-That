import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import MyBets from "./pages/MyBets";
import Digest from "./pages/Digest";
import Account from "./pages/Account";
import ResolutionAnalytics from "./pages/ResolutionAnalytics";
import ResolutionHistory from "./pages/ResolutionHistory";
import BetDetails from "./pages/BetDetails";
import Footer from "./components/Footer";
import { DISCLAIMER } from "./utils/constants";

function Header() {
  return (
    <header className="border-b bg-white">
      <div className="container py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl font-semibold">Bet-That</span>
          <span className="badge border-gray-300">LOCAL</span>
        </div>
        <nav className="flex gap-3 text-sm">
          <NavLink
            to="/"
            className={({ isActive }) => (isActive ? "underline" : "")}
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/bets"
            className={({ isActive }) => (isActive ? "underline" : "")}
          >
            My Bets
          </NavLink>
          <NavLink
            to="/resolution-analytics"
            className={({ isActive }) => (isActive ? "underline" : "")}
          >
            Analytics
          </NavLink>
          <NavLink
            to="/digest"
            className={({ isActive }) => (isActive ? "underline" : "")}
          >
            Digest
          </NavLink>
          <NavLink
            to="/account"
            className={({ isActive }) => (isActive ? "underline" : "")}
          >
            Account
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Header />
      <main className="container py-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bets" element={<MyBets />} />
          <Route path="/bets/:betId" element={<BetDetails />} />
          <Route path="/resolution-analytics" element={<ResolutionAnalytics />} />
          <Route path="/resolution-history" element={<ResolutionHistory />} />
          <Route path="/digest" element={<Digest />} />
          <Route path="/account" element={<Account />} />
        </Routes>
      </main>
      <Footer disclaimer={DISCLAIMER} />
    </BrowserRouter>
  );
}
