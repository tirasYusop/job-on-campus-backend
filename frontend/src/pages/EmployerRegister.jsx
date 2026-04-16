import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../css/EmployerRegister.css";

function EmployerRegister() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    full_name: "",
    company_name: "",
    phone_number: ""
  });

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleRegister = async () => {

    // 🔥 FRONTEND VALIDATION
    if (!form.username.trim()) return alert("Username is required");
    if (!form.email.trim()) return alert("Email is required");
    if (!form.email.includes("@")) return alert("Invalid email format");
    if (!form.password.trim()) return alert("Password is required");
    if (form.password.length < 6) return alert("Password must be at least 6 characters");

    if (!form.full_name.trim()) return alert("Full name is required");
    if (!form.company_name.trim()) return alert("Company name is required");
    if (!form.phone_number.trim()) return alert("Phone number is required");

    try {
      const res = await fetch("http://localhost:8000/api/employer-register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        credentials: "include",
        body: JSON.stringify({
          username: form.username.trim(),
          email: form.email.trim(),
          password: form.password,
          full_name: form.full_name.trim(),
          company_name: form.company_name.trim(),
          phone_number: form.phone_number.trim()
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "Registration failed");
        return;
      }

      alert("Employer registered & logged in!");

      navigate("/employer-dashboard");

    } catch (err) {
      alert("Server error: " + err.message);
    }
  };

  return (
    <div className="emp-page">

      <div className="emp-card">

        <h2 className="emp-title">🏢 Employer Register</h2>
        <p className="emp-sub">Create your company account</p>

        <div className="emp-form">

          <input
            name="email"
            type="email"
            placeholder="Email"
            value={form.email}
            onChange={handleChange}
            className="emp-input"
          />

          <input
            name="username"
            placeholder="Username"
            value={form.username}
            onChange={handleChange}
            className="emp-input"
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            value={form.password}
            onChange={handleChange}
            className="emp-input"
          />

          <input
            name="full_name"
            placeholder="Full Name"
            value={form.full_name}
            onChange={handleChange}
            className="emp-input"
          />

          <input
            name="company_name"
            placeholder="Company Name"
            value={form.company_name}
            onChange={handleChange}
            className="emp-input"
          />

          <input
            name="phone_number"
            placeholder="Phone Number"
            value={form.phone_number}
            onChange={handleChange}
            className="emp-input"
          />

        </div>

        <button className="emp-btn" onClick={handleRegister}>
          Register
        </button>

      </div>

    </div>
  );
}

export default EmployerRegister;