import React, { useEffect, useState } from "react";
import axios from "axios";
import { useNavigate, useLocation } from "react-router-dom";
import "../css/JobPost.css";

export default function JobPost() {
  const navigate = useNavigate();
  const location = useLocation();

  const editJob = location.state || null;
  const isEdit = !!editJob;

  // ✅ EMPTY TEMPLATE (IMPORTANT)
  const emptyForm = {
    job_type: "",
    business_type: "",
    phone: "",
    location: "",
    start_date: "",
    end_date: "",
    work_time: "",
    salary_estimate: "",
    num_workers: "",
    criteria: "",
  };

  const [formData, setFormData] = useState(emptyForm);

  // ✅ AUTO FILL (EDIT MODE) + RESET (CREATE MODE)
  useEffect(() => {
    if (isEdit) {
      setFormData({
        job_type: editJob.job_type || "",
        business_type: editJob.business_type || "",
        phone: editJob.phone || "",
        location: editJob.location || "",
        start_date: editJob.start_date || "",
        end_date: editJob.end_date || "",
        work_time: editJob.work_time || "",
        salary_estimate: editJob.salary_estimate || "",
        num_workers: editJob.num_workers || "",
        criteria: editJob.criteria || "",
      });
    } else {
      setFormData(emptyForm);
    }
  }, [isEdit, editJob]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // ================= SUBMIT =================
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (isEdit) {
        // 🔥 UPDATE JOB
        await axios.put(
          `http://localhost:8000/api/employer/job/update-job/${editJob.id}/`,
          formData,
          { withCredentials: true }
        );

        alert("Job updated successfully!");
      } else {
        // 🔥 CREATE JOB
        await axios.post(
          "http://localhost:8000/api/employer/post-job/",
          formData,
          { withCredentials: true }
        );

        alert("Job posted successfully!");
      }

      navigate("/employer-dashboard");

    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "Error saving job");
    }
  };

  return (
    <div className="job-page">

      {/* NAVBAR */}
      <div className="job-navbar">

        <div className="nav-left">
          <button onClick={() => navigate("/employer-dashboard")}>
            ← Back
          </button>
        </div>

        <div className="nav-center">
          <h3>{isEdit ? "Edit Job" : "Post Job"}</h3>
        </div>

      </div>

      {/* FORM */}
      <div className="job-container">

        <div className="job-card">

          <h1 className="job-title">
            {isEdit ? "✏️ Edit Job" : "📌 Post New Job"}
          </h1>

          <form onSubmit={handleSubmit} className="job-form">

            <input
              name="job_type"
              placeholder="Job Type"
              value={formData.job_type}
              onChange={handleChange}
              required
            />

            <input
              name="business_type"
              placeholder="Business Type"
              value={formData.business_type}
              onChange={handleChange}
              required
            />

            <input
              name="phone"
              placeholder="Phone Number"
              value={formData.phone}
              onChange={handleChange}
              required
            />

            <input
              name="location"
              placeholder="Location"
              value={formData.location}
              onChange={handleChange}
              required
            />

            <div className="job-row">
              <input
                type="date"
                name="start_date"
                value={formData.start_date}
                onChange={handleChange}
                required
              />

              <input
                type="date"
                name="end_date"
                value={formData.end_date}
                onChange={handleChange}
                required
              />
            </div>

            <input
              name="work_time"
              placeholder="Work Time (e.g 9AM - 5PM)"
              value={formData.work_time}
              onChange={handleChange}
              required
            />

            <input
              name="salary_estimate"
              placeholder="Salary (e.g RM100/day)"
              value={formData.salary_estimate}
              onChange={handleChange}
              required
            />

            <input
              type="number"
              name="num_workers"
              placeholder="Number of Workers"
              value={formData.num_workers}
              onChange={handleChange}
              required
            />

            <textarea
              name="criteria"
              placeholder="Job Criteria"
              value={formData.criteria}
              onChange={handleChange}
              required
            />

            <button type="submit" className="job-btn">
              {isEdit ? "Update Job" : "Post Job"}
            </button>

          </form>

        </div>

      </div>

    </div>
  );
}