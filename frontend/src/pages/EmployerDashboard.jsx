import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "../css/EmployerDashboard.css";
import logo from "../images/LOGOMPP.png";

export default function EmployerDashboard() {
  const navigate = useNavigate();

  const [verified, setVerified] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [complaintText, setComplaintText] = useState("");
  const [complaintAppId, setComplaintAppId] = useState(null);
  const fetchVerificationStatus = async () => {
    try {
      const res = await axios.get("http://localhost:8000/api/employer-status/", {
        withCredentials: true,
      });
      setVerified(res.data.verified);
    } catch (err) {
      console.error(err);
      setVerified(false);
    }
  };

  const fetchJobs = async () => {
    try {
      const res = await axios.get("http://localhost:8000/api/employer-jobs/", {
        withCredentials: true,
      });
      setJobs(res.data);
    } catch (err) {
      console.error(err);
      setJobs([]);
    }
  };

  useEffect(() => {
    fetchVerificationStatus();
    fetchJobs();

    const interval = setInterval(() => {
      fetchVerificationStatus();
      fetchJobs();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const handleLogout = async () => {
    await fetch("http://localhost:8000/api/logout/", {
      method: "POST",
      credentials: "include",
    });

    localStorage.clear();
    navigate("/");
  };

  const handlePostJob = () => {
    if (!verified) {
      alert("Your account is not verified yet.");
      return;
    }
    navigate("/employer/job-form");
  };

  const updateApplication = async (id, action) => {
    try {
      const res = await axios.post(
        `http://localhost:8000/api/confirm-application/${id}/`,
        { action },
        { withCredentials: true }
      );

      await fetchJobs();

      setSelectedJob((prev) => {
        if (!prev) return prev;

        return {
          ...prev,
          applications: prev.applications.map((app) =>
            app.id === id ? { ...app, status: res.data.status } : app
          ),
        };
      });
    } catch (err) {
      console.error(err);
    }
  };
    const submitComplaint = async () => {
      if (!complaintAppId) {
        alert("No student selected to report");
        return;
      }

      if (!complaintText.trim()) {
        alert("Please write a complaint");
        return;
      }

      try {
          await axios.post(
            `http://localhost:8000/api/employer/student-report/${complaintAppId}`,
            {
              complaint: complaintText.trim(),
            },
            {
              withCredentials: true,
              headers: {
                "Content-Type": "application/json",
              },
            }
          );

        alert("Complaint submitted successfully!");

        // reset state
        setComplaintText("");
        setComplaintAppId(null);
      } catch (err) {
        console.error("Complaint error:", err.response?.data || err.message);
        alert(err.response?.data?.error || "Failed to submit complaint");
      }
    };

    const formatTime = (date) => {
    const diff = new Date() - new Date(date);

    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(mins / 60);
    const days = Math.floor(hours / 24);

    if (mins < 1) return "Just now";
    if (mins < 60) return `${mins} minutes ago`;
    if (hours < 24) return `${hours} hours ago`;
    return `${days} days ago`;
  };

  // 🗑️ DELETE JOB
  const handleDeleteJob = async (jobId) => {
    if (!window.confirm("Delete this job?")) return;

    try {
      await axios.delete(
        `http://localhost:8000/api/employer/job/delete-job/${jobId}/`,
        { withCredentials: true }
      );

      fetchJobs();
      setSelectedJob(null);
    } catch (err) {
      console.error(err);
    }
  };

  // ✏️ EDIT JOB
  const handleEditJob = (job) => {
    navigate(`/employer/job-form`, { state: job }); // pass job data
  };

  return (
    <div className="empD-page">
      {/* NAVBAR */}
      <div className="empD-navbar">

        <div className="empD-left">
          <div className="logo">
              <img src={logo} alt="Logo" />
            </div>
        </div>

        <h2 className="empD-title">JOB ON CAMPUS UMS (EMPLOYER) </h2>

        <div className="empD-right">
          <button className="empD-logout" onClick={handleLogout}>
            Logout
          </button>
        </div>

      </div>

      {/* HERO */}
      <div className="empD-hero">
        <div>
          <h2>{verified ? "Verified Employer ✅" : "Pending Verification ⏳"}</h2>
          <p>Manage your jobs and applicants</p>
        </div>

        <button
          className="empD-post"
          onClick={handlePostJob}
          disabled={!verified}
        >
          ➕ Post Job
        </button>
      </div>

      {/* JOB LIST */}
      <div className="empD-grid">
        {jobs.length === 0 ? (
          <p className="empty-text">No jobs posted yet.</p>
        ) : (
          jobs.map((job) => (
            <div
              key={job.id} // ✅ FIXED
              className="empD-card"
              onClick={() => setSelectedJob(job)}
            >
              {job.total_applicants > 0 && (
                <div className="empD-badge">
                  {job.total_applicants}
                </div>
              )}

              <h3>
                {job.job_type} • {job.location}
              </h3>
              <p>{formatTime(job.created_at)}</p>

              <p className="hint">Click to view applicants</p>
            </div>
          ))
        )}
      </div>

      {/* JOB MODAL */}
      {selectedJob && (
        <div className="empD-modal" onClick={() => setSelectedJob(null)}>
          <div
            className="empD-modal-box"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Applicants</h2>

            {/* ✏️ EDIT + DELETE */}
            <div style={{ marginBottom: "10px" }}>
              <button onClick={() => handleEditJob(selectedJob)}>
                ✏️ Edit Job
              </button>

              <button
                style={{ marginLeft: "10px", background: "red", color: "white" }}
                onClick={() => handleDeleteJob(selectedJob.id)}
              >
                🗑️ Delete Job
              </button>
            </div>

            {(selectedJob?.applications || []).length === 0 ? (
              <p>No applicants yet</p>
            ) : (
              selectedJob.applications.map((app) => (
                <div
                  key={app.id}
                  className="empD-app-card"
                  onClick={() => setSelectedStudent(app)}
                  style={{ cursor: "pointer" }}
                >
                  {/* ✅ FIXED */}
                  <p>👤 {app.student?.nama_penuh}</p>
                  <p>Status: {app.status}</p>

                  {/* ✅ SHOW COMPLAINT */}
                  {app.complaint && (
                    <div
                      style={{
                        marginTop: "8px",
                        padding: "8px",
                        background: "#ffe6e6",
                        borderRadius: "6px",
                        fontSize: "13px"
                      }}
                    >
                      <b>Complaint:</b> {app.complaint}
                    </div>
                  )}

                  {/* ✅ SHOW STATUS */}
                  {app.complaint_status === "reported" && (
                    <p style={{ color: "red", fontSize: "12px" }}>
                      ⚠️ Report submitted
                    </p>
                  )}
                  {app.status === "confirmed" && (
                    <button
                      style={{
                        marginTop: "5px",
                        background: "red",
                        color: "white",
                        border: "none",
                        padding: "5px 10px",
                        borderRadius: "6px",
                        cursor: "pointer"
                      }}
                      onClick={(e) => {
                        e.stopPropagation();
                        setComplaintAppId(app.id);
                      }}
                    >
                      Report Student
                    </button>
                  )}

                  {app.status === "pending" ? (
                    <div className="empD-actions">
                      <button
                        className="btn-accept"
                        onClick={(e) => {
                          e.stopPropagation();
                          updateApplication(app.id, "confirm");
                        }}
                      >
                        Accept
                      </button>

                      <button
                        className="btn-reject"
                        onClick={(e) => {
                          e.stopPropagation();
                          updateApplication(app.id, "reject");
                        }}
                      >
                        Reject
                      </button>
                    </div>
                  ) : (
                    <p className={`status ${app.status}`}>
                      {app.status === "confirmed" ? "Accepted" : "Rejected"}
                    </p>
                  )}
                </div>
              ))
            )}

            <button
              className="close-btn"
              onClick={() => setSelectedJob(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {/* STUDENT DETAILS */}
      {selectedStudent && (
        <div
          className="empD-modal"
          onClick={() => setSelectedStudent(null)}
        >
          <div
            className="empD-modal-box"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Student Details</h2>

            <p><b>Full Name:</b> {selectedStudent.student?.nama_penuh}</p>
            <p><b>Username:</b> {selectedStudent.student?.username}</p>
            <p><b>Matric No:</b> {selectedStudent.student?.no_matrik}</p>
            <p><b>Phone:</b> {selectedStudent.student?.no_telefon}</p>
            <p><b>Faculty:</b> {selectedStudent.student?.fakulti}</p>
            <p><b>College:</b> {selectedStudent.student?.kolej}</p>

            <p><b>Status:</b> {selectedStudent.status}</p>

            <button
              className="close-btn"
              onClick={() => setSelectedStudent(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}

      {complaintAppId && (
        <div className="empD-modal" onClick={() => setComplaintAppId(null)}>
          <div
            className="empD-modal-box"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Report Student</h2>

            <textarea
              placeholder="Write your complaint here..."
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              style={{ width: "100%", height: "120px" }}
            />

            <div style={{ marginTop: "10px" }}>
              <button
                onClick={submitComplaint}
                style={{
                  background: "red",
                  color: "white",
                  padding: "8px 12px",
                  border: "none",
                  borderRadius: "6px",
                  marginRight: "10px"
                }}
              >
                Submit
              </button>

              <button
                onClick={() => setComplaintAppId(null)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}