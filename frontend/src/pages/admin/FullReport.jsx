import { useEffect, useState } from "react";
import { Bar, Pie } from "react-chartjs-2";

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
} from "chart.js";

import "../../css/AdminPages.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

function FullReport() {
  const [data, setData] = useState(null);

  const [feedbackList, setFeedbackList] = useState([]);
  const [complaintList, setComplaintList] = useState([]);
  const [modalType, setModalType] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/admin/full-report/")
      .then(res => res.json())
      .then(setData)
      .catch(err => console.error(err));
  }, []);

  const openFeedback = async () => {
    const res = await fetch("http://localhost:8000/api/admin/feedback-list/");
    const result = await res.json();
    setFeedbackList(result);
    setModalType("feedback");
  };

  const openComplaint = async () => {
    const res = await fetch("http://localhost:8000/api/admin/complaint-list/");
    const result = await res.json();
    setComplaintList(result);
    setModalType("complaint");
  };

  if (!data) return <p>Loading analytics...</p>;

  const safeAccepted = data.weekly_accepted || [];
  const safeCancelled = data.weekly_cancelled || [];
  const safeFaculty = data.faculty_stats || [];
  const safeCollege = data.college_stats || [];

  const acceptedChart = {
    labels: safeAccepted.map(w => w.date),
    datasets: [
      {
        label: "Accepted",
        data: safeAccepted.map(w => w.total_accepted),
        backgroundColor: "#4f46e5",
      }
    ]
  };

  const cancelledChart = {
    labels: safeCancelled.map(w => w.date),
    datasets: [
      {
        label: "Cancelled",
        data: safeCancelled.map(w => w.total_cancelled),
        backgroundColor: "#ef4444",
      }
    ]
  };

  const facultyChart = {
    labels: safeFaculty.map(f => f.fakulti),
    datasets: [
      {
        data: safeFaculty.map(f => f.total),
        backgroundColor: ["#6366f1", "#22c55e", "#f59e0b", "#ef4444", "#0ea5e9"],
      }
    ]
  };

  const collegeChart = {
    labels: safeCollege.map(c => c.kolej),
    datasets: [
      {
        data: safeCollege.map(c => c.total),
        backgroundColor: ["#8b5cf6", "#10b981", "#f97316", "#e11d48", "#06b6d4"],
      }
    ]
  };

  return (
    <div className="admin-page">

      <h2>📊 Analytics Dashboard</h2>

      {/* KPI */}
      <div className="stats-grid">
        <div className="stat-card"><h3>{data.total_users}</h3><p>Total Users</p></div>
        <div className="stat-card"><h3>{data.total_students}</h3><p>Students</p></div>
        <div className="stat-card"><h3>{data.active_jobs}</h3><p>Active Jobs</p></div>
        <div className="stat-card"><h3>{data.expired_jobs}</h3><p>Expired Jobs</p></div>
        <div className="stat-card"><h3>{data.total_employers}</h3><p>Employers</p></div>

        <div className="stat-card" onClick={openFeedback} style={{ cursor: "pointer" }}>
          <h3>{data.total_feedback}</h3>
          <p>Student Feedback</p>
        </div>

        <div className="stat-card" onClick={openComplaint} style={{ cursor: "pointer" }}>
          <h3>{data.total_complaints}</h3>
          <p>Employer Complaints</p>
        </div>

        <div className="stat-card"><h3>{data.total_applications}</h3><p>Total Applications</p></div>
        <div className="stat-card"><h3>{data.total_jobs}</h3><p>Total Jobs</p></div>
        <div className="stat-card"><h3>{data.total_cancelled}</h3><p>Cancelled</p></div>
        <div className="stat-card"><h3>{data.cancel_rate}%</h3><p>Cancel Rate</p></div>
        <div className="stat-card"><h3>{data.cancel_rate}%</h3><p>Cancel Rate</p></div>
      </div>

      {/* CHARTS */}
      <div className="charts-grid">
        <div className="chart-card"><h3>📅 Weekly Accepted</h3><Bar data={acceptedChart} /></div>
        <div className="chart-card"><h3>❌ Weekly Cancelled</h3><Bar data={cancelledChart} /></div>
        <div className="chart-card"><h3>🎓 Faculty Distribution</h3><Pie data={facultyChart} /></div>
        <div className="chart-card"><h3>🏫 College Distribution</h3><Pie data={collegeChart} /></div>
      </div>

      {/* ✅ MODAL FIXED (INSIDE RETURN) */}
      {modalType && (
        <div className="modal-backdrop" onClick={() => setModalType(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>

            <h3>
              {modalType === "feedback" ? "Student Feedback" : "Employer Complaints"}
            </h3>

            <div className="modal-content">
              {modalType === "feedback" &&
                feedbackList.map(f => (
                  <div key={f.id}>
                    <b>{f.student}</b>
                    <p>{f.feedback}</p>
                  </div>
                ))
              }

              {modalType === "complaint" &&
                complaintList.map(c => (
                  <div key={c.id}>
                    <b>{c.student}</b>
                    <p>{c.complaint}</p>
                  </div>
                ))
              }
            </div>

            <button onClick={() => setModalType(null)}>Close</button>
          </div>
        </div>
      )}

    </div>
  );
}

export default FullReport;