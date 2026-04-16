import React, { useEffect, useState } from "react";
import axios from "axios";
import { useParams } from "react-router-dom";

export default function Applicants() {
  const { jobId } = useParams();
  const [apps, setApps] = useState([]);

  useEffect(() => {
    axios
      .get(`http://localhost:8000/api/job-applicants/${jobId}/`)
      .then((res) => setApps(res.data))
      .catch((err) => console.error(err));
  }, [jobId]);

  const updateStatus = async (id, status) => {
    await axios.post(
      `http://localhost:8000/api/update-application/${id}/`,
      { status }
    );
    alert("Updated!");
    window.location.reload();
  };

  return (
    <div style={{ padding: "30px" }}>
      <h2>Applicants</h2>

      {apps.map((app) => (
        <div
          key={app.id}
          style={{
            padding: "15px",
            marginBottom: "10px",
            border: "1px solid #ccc",
            borderRadius: "10px",
          }}
        >
          <p><strong>Name:</strong> {app.student_name}</p>
          <p><strong>Status:</strong> {app.status}</p>

          <button
            onClick={() => updateStatus(app.id, "confirmed")}
            style={{
              marginRight: "10px",
              background: "green",
              color: "#fff",
            }}
          >
            Accept
          </button>

          <button
            onClick={() => updateStatus(app.id, "rejected")}
            style={{
              background: "red",
              color: "#fff",
            }}
          >
            Reject
          </button>
        </div>
      ))}
    </div>
  );
}