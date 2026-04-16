import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../css/StudentDashboard.css";
import logo from "../images/LOGOMPP.png";

export default function StudentDashboard() {
  const [openSection, setOpenSection] = useState(null);
  const navigate = useNavigate();

  const [jobs, setJobs] = useState([]);
  const [applications, setApplications] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [confirmJob, setConfirmJob] = useState(null);
  const [confirmCancel, setConfirmCancel] = useState(null);
  const [search, setSearch] = useState("");
  const [feedbackAppId, setFeedbackAppId] = useState(null);
  const [feedbackText, setFeedbackText] = useState("");
  const [pastJobs, setPastJobs] = useState([]);

  const toggleSection = (section) => {
  setOpenSection(openSection === section ? null : section);
};

  const filteredJobs = jobs.filter(job => {
    const keyword = search.toLowerCase();

    return (
      job.job_type.toLowerCase().includes(keyword) ||
      job.business_type.toLowerCase().includes(keyword) ||
      job.location.toLowerCase().includes(keyword)
    );
  });

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await axios.get("http://localhost:8000/api/jobs/");
        setJobs(res.data);
      } catch (err) {
        console.error(err);
      }
    };
    fetchJobs();
  }, []);

  useEffect(() => {
  const now = new Date();

  const past = applications.filter(a => {
    if (a.status !== "confirmed") return false;

    // try find job end_date from jobs list
    const job = jobs.find(j => j.id === a.job_id);

    if (!job || !job.end_date) return false;

    return new Date(job.end_date) < now;
  });

  setPastJobs(past);
}, [applications, jobs]);

  useEffect(() => {
    const fetchApplications = async () => {
      try {
        const res = await axios.get(
          "http://localhost:8000/api/student-applications/",
          { withCredentials: true }
        );
        setApplications(res.data);
      } catch (err) {
        console.error(err);
      }
    };

    fetchApplications();
    const interval = setInterval(fetchApplications, 5000);
    return () => clearInterval(interval);
  }, []);

  const applyJob = async (jobId) => {
    try {
      await axios.post(
        `http://localhost:8000/api/apply-job/${jobId}/`,
        {},
        { withCredentials: true }
      );

      const res = await axios.get(
        "http://localhost:8000/api/student-applications/",
        { withCredentials: true }
      );

      setApplications(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  // =========================
  // CANCEL APPLICATION
  // =========================
  const cancelApplication = async (jobId) => {
    try {
      await axios.delete(
        `http://localhost:8000/api/cancel-application/${jobId}/`,
        { withCredentials: true }
      );

      setApplications(prev =>
        prev.filter(app => Number(app.job_id) !== Number(jobId))
      );
    } catch (err) {
      console.error(err);
    }
  };

  // =========================
  // LOGOUT
  // =========================
  const handleLogout = async () => {
    await axios.post(
      "http://localhost:8000/api/logout/",
      {},
      { withCredentials: true }
    );

    localStorage.clear();
    navigate("/");
  };

  // =========================
  // TIME AGO
  // =========================
  const timeAgo = (dateString) => {
    const now = new Date();
    const posted = new Date(dateString);
    const diff = Math.floor((now - posted) / 1000);

    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
  };

    const submitFeedback = async () => {
    if (!feedbackText.trim()) return;

    try {
      await axios.post(
        `http://localhost:8000/api/student/submit-feedback/${feedbackAppId}/`,
        { feedback: feedbackText },
        { withCredentials: true }
      );

      alert("Feedback submitted!");

      setFeedbackAppId(null);
      setFeedbackText("");

      // refresh
      const res = await axios.get(
        "http://localhost:8000/api/student-applications/",
        { withCredentials: true }
      );
      setApplications(res.data);

    } catch (err) {
      console.error(err);
    }
  };

  // =========================
  // FILTERS
  // =========================
  const accepted = applications.filter(a => a.status === "confirmed");
  const rejected = applications.filter(a => a.status === "rejected");
  const pending = applications.filter(a => a.status === "pending");

  const appliedJobsSet = new Set(applications.map(a => Number(a.job_id)));

  return (
    <div className="dashboard-layout">

      {/* ================= TOP BAR ================= */}
      <div className="navbar">
        <div className="nav-left">
          <div className="logo">
            <img src={logo} alt="Logo" />
          </div>
        </div>

        <h3 className="nav-title">JOB ON CAMPUS UMS (STUDENT)</h3>

        <div className="nav-right">
          <button className="logout-btn" onClick={handleLogout}>
            Logout
          </button>
        </div>
      </div>

      {/* ================= MAIN (70/30) ================= */}
      <div className="dashboard-body">

        {/* ============ LEFT CONTENT (70%) ============ */}
        <div className="dashboard-content">

          {/* SEARCH */}
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search job, company, location..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* JOB LIST */}
          <div className="container-joblist">

            {[...filteredJobs]
              .sort((a, b) => b.id - a.id)
              .map(job => {
                const isApplied = appliedJobsSet.has(Number(job.id));

                return (
                  <div
                    className="jobList-card"
                    key={job.id}
                    onClick={() => setSelectedJob(job)}
                  >

                    {/* HEADER */}
                    <div className="job-header">

                      <div>
                        <h3>{job.job_type}</h3>
                        <p className="company">{job.business_type}</p>
                      </div>

                      <div className="job-time">
                        🕒 {timeAgo(job.created_at)}
                      </div>

                    </div>

                    <p>📍LOCATION {job.location}</p>
                    <p>DATE: {job.start_date} SEHINGGA {job.end_date}</p>
                    <p>🕒 TIME: {job.work_time}</p>
                    <p>SALARY : {job.salary_estimate}</p>
                    <p> WORKER : {job.num_workers}</p>
                    <p> CRITERIA : {job.criteria}</p>
                    

       


                    <button
                      className={`apply-btn ${isApplied ? "disabled" : ""}`}
                      disabled={isApplied}
                      onClick={(e) => {
                        e.stopPropagation();
                        setConfirmJob(job);
                      }}
                    >
                      {isApplied ? "Applied" : "Apply Job"}
                    </button>

                  </div>
                );
              })}
          </div>
        </div>

  {/* ============ RIGHT NOTIFICATION (30%) ============ */}
        <div className="dashboard-notification">

          <h3>DASHBOARD</h3>

          {/* ACCEPTED */}
          <div onClick={() => toggleSection("accepted")} className="title accepted">
            🟢 Accepted
          </div>

          {openSection === "accepted" &&
            accepted.map(a => (
              <p
                key={a.id}
                style={{ cursor: "pointer" }}
                onClick={async () => {
                  const res = await axios.get("http://localhost:8000/api/jobs/");
                  const job = res.data.find(j => j.id === a.job_id);
                  if (job) setSelectedJob(job);
                }}
              >
                {a.job_type}
              </p>
            ))
          }

          <div onClick={() => toggleSection("rejected")} className="title rejected">
            🔴 Rejected
          </div>

          {openSection === "rejected" &&
            rejected.map(a => (
              <p key={a.id}>🔴 {a.job_type}</p>
            ))
          }

          <div onClick={() => toggleSection("pending")} className="title pending">
            🟡 Pending
          </div>

          {openSection === "pending" &&
            pending.map(a => (
              <div key={a.id} className="pending-item">
                <span>{a.job_type}</span>

                <button
                  className="cancel-mini-btn"
                  onClick={() => setConfirmCancel(a.job_id)}
                >
                  Cancel
                </button>
              </div>
            ))
          }

          <div onClick={() => toggleSection("past")} className="title">
            📌 Past Jobs
          </div>

          {openSection === "past" &&
            (pastJobs.length === 0 ? (
              <p>No past jobs</p>
            ) : (
              pastJobs.map(a => (
                <div key={a.id} style={{ marginBottom: "8px" }}>
                  <span>✔ {a.job_type}</span>

                  <button
                    style={{
                      marginLeft: "10px",
                      background: "green",
                      color: "white",
                      border: "none",
                      padding: "4px 8px",
                      borderRadius: "5px",
                      cursor: "pointer"
                    }}
                    onClick={() => setFeedbackAppId(a.id)}
                  >
                    Give Feedback
                  </button>
                </div>
              ))
            ))
          }

        </div>
      </div>

      
      {/* ================= FEEDBACK MODAL ================= */}
      {feedbackAppId && (
        <div className="modal-overlay" onClick={() => setFeedbackAppId(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>

            <h2>Give Feedback</h2>

            <textarea
              value={feedbackText}
              onChange={(e) => setFeedbackText(e.target.value)}
              placeholder="Write your feedback..."
              style={{ width: "100%", height: "120px" }}
            />

            <div className="modal-actions">
              <button className="confirm-btn" onClick={submitFeedback}>
                Submit
              </button>

              <button
                className="cancel-btn"
                onClick={() => setFeedbackAppId(null)}
              >
                Cancel
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ================= APPLY MODAL ================= */}
      {confirmJob && (
        <div className="modal-overlay" onClick={() => setConfirmJob(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>

            <h2>⚠️ Confirm Apply</h2>
            <h3>{confirmJob.job_type}</h3>

            <div className="modal-actions">
              <button
                className="confirm-btn"
                onClick={() => {
                  applyJob(confirmJob.id);
                  setConfirmJob(null);
                }}
              >
                Yes
              </button>

              <button
                className="cancel-btn"
                onClick={() => setConfirmJob(null)}
              >
                No
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ================= CANCEL MODAL ================= */}
      {confirmCancel && (
        <div className="modal-overlay" onClick={() => setConfirmCancel(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>

            <h2>Cancel Application?</h2>

            <div className="modal-actions">
              <button
                className="confirm-btn danger"
                onClick={() => {
                  cancelApplication(confirmCancel);
                  setConfirmCancel(null);
                }}
              >
                Yes
              </button>

              <button
                className="cancel-btn"
                onClick={() => setConfirmCancel(null)}
              >
                No
              </button>
            </div>

          </div>
        </div>
      )}

      {/* ================= JOB DETAILS MODAL ================= */}
      {selectedJob && (
        <div className="modal-overlay" onClick={() => setSelectedJob(null)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>

            <h2>{selectedJob.job_type}</h2>

            <p><b>Company:</b> {selectedJob.business_type}</p>
            <p><b>Location:</b> {selectedJob.location}</p>
            <p><b>Phone:</b> {selectedJob.phone}</p>
            <p><b>Salary:</b> {selectedJob.salary_estimate}</p>
            <p><b>Time:</b> {selectedJob.work_time}</p>

            <button
              className="close-btn"
              onClick={() => setSelectedJob(null)}
            >
              Close
            </button>

          </div>
        </div>
      )}

    </div>
  );
}