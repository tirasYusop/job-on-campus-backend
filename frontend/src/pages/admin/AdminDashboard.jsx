import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../css/AdminDashboard.css";

function AdminDashboard() {
  const navigate = useNavigate();

  const [employers, setEmployers] = useState([]);
  const [stats, setStats] = useState(null);

  // AUTH
  useEffect(() => {
    const role = localStorage.getItem("role");
    if (role !== "admin") navigate("/login");
  }, [navigate]);

  // LOGOUT
  const handleLogout = async () => {
    await fetch("http://localhost:8000/api/logout/", {
      method: "POST",
      credentials: "include",
    });

    localStorage.removeItem("role");
    navigate("/");
  };

  // FETCH UNVERIFIED
  const fetchEmployers = async () => {
    const res = await fetch("http://localhost:8000/api/admin/employers/unverified/");
    const data = await res.json();
    setEmployers(data);
  };

  // FETCH STATS (NEW 🔥)
  const fetchStats = async () => {
    const res = await fetch("http://localhost:8000/api/admin/full-report/");
    const data = await res.json();

    setStats(data);
  };

  useEffect(() => {
    fetchEmployers();
    fetchStats();
  }, []);

  const verifyEmployer = async (id) => {
    await fetch(`http://localhost:8000/api/admin/verify-employer/${id}/`, {
      method: "POST",
    });

    alert("Employer verified!");
    fetchEmployers();
    fetchStats();
  };

  return (
    <div className="admin-page">

      {/* NAVBAR */}
      <div className="admin-navbar">

        <div className="nav-left">
          🛡️ <span>Admin Panel</span>
        </div>

        <div className="nav-right">
          <button className="logout-btn" onClick={handleLogout}>
            Logout 🚪
          </button>
        </div>

      </div>

      {/* CONTENT */}
      <div className="admin-content">

        {/* =========================
            KPI DASHBOARD
        ========================= */}
        <div className="kpi-grid">

          <div className="kpi-card">
            <h3>{stats?.total_users || 0}</h3>
            <p>Total Users</p>
          </div>

          <div className="kpi-card">
            <h3>{stats?.total_students || 0}</h3>
            <p>Students</p>
          </div>

          <div className="kpi-card">
            <h3>{stats?.total_employers || 0}</h3>
            <p>Employers</p>
          </div>

          <div className="kpi-card danger">
            <h3>{employers.length}</h3>
            <p>Pending Verification</p>
          </div>

        </div>

        {/* =========================
            QUICK ACTIONS
        ========================= */}
        <div className="quick-actions">

          <div className="action-card" onClick={() => navigate("/admin/student-report")}>
            👤 Manage Users
          </div>

          <div className="action-card" onClick={() => navigate("/admin/full-report")}>
            📊 View Analytics
          </div>

          <div className="action-card" onClick={() => navigate("/admin/employer-report")}>
            🏢 Manage Employers
          </div>

        </div>

        {/* =========================
            UNVERIFIED EMPLOYERS
        ========================= */}
        <h2 className="section-title">⛔ Pending Employers</h2>

        <div className="grid">

          {employers.length === 0 ? (
            <p className="empty">No pending employers 🎉</p>
          ) : (
            employers.slice(0, 4).map((emp) => (
              <div key={emp.id} className="emp-card">
                <h3>{emp.company_name}</h3>
                <p>👤 {emp.username}</p>
                <p>📞 {emp.phone_number}</p>

                <button
                  className="verify-btn"
                  onClick={() => verifyEmployer(emp.id)}
                >
                  ✅ Verify
                </button>
              </div>
            ))
          )}

        </div>

      </div>
    </div>
  );
}

export default AdminDashboard;