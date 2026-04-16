import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../css/Login.css";

function Login() {
  const navigate = useNavigate();

  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          login_id: loginId,   // ✅ Student ID / Username / Email
          password: password
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "Login failed");
        return;
      }

      // save session
      localStorage.setItem("role", data.role);
      localStorage.setItem("user", JSON.stringify(data));

      // redirect based on role
      if (data.role === "admin") {
        navigate("/admin-dashboard");
      } else if (data.role === "student") {
        navigate("/student-dashboard");
      } else if (data.role === "employer") {
        navigate("/employer-dashboard");
      }

    } catch (err) {
      alert("Server error");
    }
  };

  return (
    <div className="login-page">

      <div className="login-card animate-card">

        <h2 className="login-title">🔐 Login</h2>
        <p className="login-sub">Welcome to Job Campus, Please Sign In.</p>

        <div className="login-form">

          {/* LOGIN ID (Student ID / Username / Email) */}
          <input
            className="login-input"
            id="loginId"
            name="loginId"
            autoComplete="username"
            placeholder="Student ID / Username / Email"
            value={loginId}
            onChange={(e) => setLoginId(e.target.value)}
          />

          {/* PASSWORD */}
          <input
            className="login-input"
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

        </div>

        <button className="login-btn" onClick={handleLogin}>
          Login
        </button>

        <button
          className="login-register-btn"
          onClick={() => navigate("/register")}
        >
          Create Account
        </button>

      </div>

    </div>
  );
}

export default Login;