import { useEffect, useState } from "react";

function UsersPage() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/api/admin/users/")
      .then(res => res.json())
      .then(data => setUsers(data));
  }, []);

  return (
    <div>
      <h2>👤 All Users</h2>

      {users.map(u => (
        <div key={u.id}>
          <p>{u.username} ({u.role}) - {u.verified ? "✅ Verified" : "❌"}</p>
        </div>
      ))}
    </div>
  );
}

export default UsersPage;