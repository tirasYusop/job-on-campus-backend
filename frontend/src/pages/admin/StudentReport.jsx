import { useEffect, useState } from "react";
import "../../css/AdminPages.css";

function StudentsPage() {
  const [students, setStudents] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [faculty, setFaculty] = useState("ALL");

  useEffect(() => {
    fetch("http://localhost:8000/api/admin/students/")
      .then(res => res.json())
      .then(data => {
        setStudents(data);
        setFiltered(data);
      });
  }, []);

  // 🎯 FILTER LOGIC
  useEffect(() => {
    if (faculty === "ALL") {
      setFiltered(students);
    } else {
      setFiltered(
        students.filter(s => s.fakulti === faculty)
      );
    }
  }, [faculty, students]);

  // 🔥 GET UNIQUE FACULTIES
  const faculties = ["ALL", ...new Set(students.map(s => s.fakulti))];

  return (
    <div className="admin-page">

      <div className="admin-header">
        <h2>🎓 Students Management</h2>

        <select
          value={faculty}
          onChange={(e) => setFaculty(e.target.value)}
          className="filter-dropdown"
        >
          {faculties.map((f, i) => (
            <option key={i} value={f}>{f}</option>
          ))}
        </select>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Matric</th>
              <th>Faculty</th>
              <th>College</th>
              <th>Phone</th>
            </tr>
          </thead>

          <tbody>
            {filtered.map((s) => (
              <tr key={s.id}>
                <td>{s.nama_penuh}</td>
                <td>{s.no_matrik}</td>
                <td>{s.fakulti}</td>
                <td>{s.kolej}</td>
                <td>{s.no_telefon}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

    </div>
  );
}

export default StudentsPage;