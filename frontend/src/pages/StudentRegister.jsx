import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../css/StudentRegister.css";

function StudentRegister() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    nama_penuh: "",
    no_matrik: "",
    no_telefon: "",
    fakulti: "",
    kolej: ""
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleRegister = async () => {
    if (!form.email.endsWith("@iluv.ums.edu.my")) {
      alert("Only UMS student email allowed (@iluv.ums.edu.my)");
      return;
    }

    if (!form.username || !form.password) {
      alert("Username and password required");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/api/student-register/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(form),
      });

      const data = await res.json();

      if (!res.ok) {
        alert(data.error || "Request failed");
        return;
      }

      alert("Registration successful!");

      setTimeout(() => {
        navigate("/student-dashboard");
      }, 300);

    } catch (err) {
      alert(err.message);
    }
  };

  return (
    <div className="stu-page">

      <div className="stu-card animate-card">

        <h2 className="stu-title">🎓 Student Register</h2>
        <p className="stu-sub">Create your account to start applying jobs</p>

        <div className="stu-form">

          {/* USERNAME (UPDATED LABEL) */}
          <input
            name="username"
            placeholder="Username"
            onChange={handleChange}
            className="stu-input"
          />

          {/* EMAIL */}
          <input
            name="email"
            type="email"
            placeholder="Student Email (@iluv.ums.edu.my)"
            onChange={handleChange}
            className="stu-input"
          />

          {/* PASSWORD */}
          <input
            name="password"
            type="password"
            placeholder="Password"
            onChange={handleChange}
            className="stu-input"
          />

          {/* FULL NAME */}
          <input
            name="nama_penuh"
            placeholder="Full Name"
            onChange={handleChange}
            className="stu-input"
          />

          {/* MATRIC */}
          <input
            name="no_matrik"
            placeholder="Matric Number"
            onChange={handleChange}
            className="stu-input"
          />

          {/* PHONE */}
          <input
            name="no_telefon"
            placeholder="Phone Number"
            onChange={handleChange}
            className="stu-input"
          />

          {/* FAKULTI */}
          <select
            name="fakulti"
            onChange={handleChange}
            className="stu-input"
          >
            <option value="">Select Fakulti</option>
            <option value="fpsk">FPSK</option>
            <option value="fst">FST</option>
            <option value="fsmp">FSMP</option>
            <option value="fki">FKI</option>
            <option value="fkj">FKJ</option>
            <option value="fis">FIS</option>
            <option value="fpt">FPT</option>
            <option value="fssk">FSSK</option>
            <option value="fpps">FPPS</option>
            <option value="fpks">FPKS</option>
            <option value="astif">ASTIF</option>
            <option value="fpep">FPEP</option>
          </select>

          {/* KOLEJ */}
          <select
            name="kolej"
            onChange={handleChange}
            className="stu-input"
          >
            <option value="">Select Kolej</option>
            <option value="kktpar">KKTPAR</option>
            <option value="kktf">KKTF</option>
            <option value="kktm">KKTM</option>
            <option value="kku1b">KKU1B</option>
            <option value="kkakf">KKAKF</option>
            <option value="kknr">KKNR</option>
          </select>

        </div>

        <button className="stu-btn" onClick={handleRegister}>
          Register
        </button>

      </div>

    </div>
  );
}

export default StudentRegister;