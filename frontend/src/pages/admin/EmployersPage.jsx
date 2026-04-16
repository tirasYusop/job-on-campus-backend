import { useEffect, useState } from "react";
import "../../css/AdminPages.css";

function EmployersPage() {
  const [employers, setEmployers] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [status, setStatus] = useState("ALL");

  useEffect(() => {
    fetch("http://localhost:8000/api/admin/employers/")
      .then(res => res.json())
      .then(data => {
        setEmployers(data);
        setFiltered(data);
      });
  }, []);

  // 🎯 FILTER LOGIC
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
              <tr key={e.id}>
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

    </div>
  );
}

export default EmployersPage;