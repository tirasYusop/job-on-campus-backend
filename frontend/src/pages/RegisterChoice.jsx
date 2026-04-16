import { useNavigate } from "react-router-dom";
import "../css/RegisterChoice.css";

function RegisterChoice() {
  const navigate = useNavigate();

  return (
    <div className="choice-page">

      <div className="choice-card animate-card">

        <h2 className="choice-title">Create Account</h2>
        <p className="choice-sub">Select your account type</p>

        <div className="choice-buttons">

          <button
            className="choice-btn student"
            onClick={() => navigate("/register/student")}
          >
            🎓 Student
          </button>

          <button
            className="choice-btn employer"
            onClick={() => navigate("/register/employer")}
          >
            🏢 Employer
          </button>

        </div>

      </div>

    </div>
  );
}

export default RegisterChoice;