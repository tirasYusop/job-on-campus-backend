import { useEffect, useState } from "react";
import "../../css/AdminPages.css";

function EmployersPage() {
  const [employers, setEmployers] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [status, setStatus] = useState("ALL");

  // ✅ NEW: modal state
  const [selectedEmployer, setSelectedEmployer] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/admin/employers/")
      .then(res => res.json())
      .then(data => {
        setEmployers(data);
        setFiltered(data);
      });
  }, []);

  useEffect(() => {
    if (status === "ALL") {
      setFiltered(employers);
    } else if (status === "VERIFIED") {
      setFiltered(employers.filter(e => e.verified));
    } else {
      setFiltered(employers.filter(e => !e.verified));
    }
  }, [status, employers]);

  return (
    <div className="admin-page">

      {/* HEADER */}
      <div className="admin-header">
        <h2>🏢 Employers Management</h2>

        <select
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          className="filter-dropdown"
        >
          <option value="ALL">All</option>
          <option value="VERIFIED">Verified</option>
          <option value="UNVERIFIED">Unverified</option>
        </select>
      </div>

      {/* TABLE */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Username</th>
              <th>Phone</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((e) => (
              <tr
                key={e.id}
                style={{ cursor: "pointer" }}
                onClick={() => setSelectedEmployer(e)}   // ✅ OPEN MODAL
              >
                <td>{e.company_name}</td>
                <td>{e.username}</td>
                <td>{e.phone_number}</td>
                <td>
                  {e.verified ? (
                    <span className="status verified">✅ Verified</span>
                  ) : (
                    <span className="status unverified">❌ Unverified</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>


      {selectedEmployer && (
        <div className="modal-overlay" onClick={() => setSelectedEmployer(null)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>

            <h2>🏢 Employer Details</h2>

            <p><b>Company:</b> {selectedEmployer.company_name}</p>
            <p><b>Username:</b> {selectedEmployer.username}</p>
            <p><b>Full Name:</b> {selectedEmployer.full_name}</p>
            <p><b>Phone:</b> {selectedEmployer.phone_number}</p>
            <p>
              <b>Status:</b>{" "}
              {selectedEmployer.verified ? "✅ Verified" : "❌ Unverified"}
            </p>

            <button
              className="close-btn"
              onClick={() => setSelectedEmployer(null)}
            >
              Close
            </button>

          </div>
        </div>
      )}

    </div>
  );
}

export default EmployersPage;