import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Login from "./pages/Login";
import RegisterChoice from "./pages/RegisterChoice";

import StudentRegister from "./pages/StudentRegister";
import EmployerRegister from "./pages/EmployerRegister";

import StudentDashboard from "./pages/StudentDashboard";
import EmployerDashboard from "./pages/EmployerDashboard";

import AdminDashboard from "./pages/admin/AdminDashboard";
import JobPost from "./pages/JobPost";

import UsersPage from "./pages/admin/UsersPage";
import EmployersPage from "./pages/admin/EmployersPage";
import StudentReport from "./pages/admin/StudentReport";
import EmployerReport from "./pages/admin/EmployerReport";
import FullReport from "./pages/admin/FullReport";




function App() {
  return (
    <Router>
      <Routes>
        {/* AUTH */}
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<RegisterChoice />} />

        {/* REGISTER */}
        <Route path="/register/student" element={<StudentRegister />} />
        <Route path="/register/employer" element={<EmployerRegister />} />

        {/* DASHBOARD */}
        <Route path="/student-dashboard" element={<StudentDashboard />} />
        <Route path="/employer-dashboard" element={<EmployerDashboard />} />

        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<div>Users Page</div>} />
        <Route path="/admin/employers" element={<div>Employers Page</div>} />
        <Route path="/admin/reports" element={<div>Reports Page</div>} />
        <Route path="/employer/job-form" element={<JobPost />} />
        <Route path="/post-job" element={<JobPost />} />
        <Route path="/student-dashboard/job/:id" element={<div>Job Details Page</div>} />  
        <Route path="/student-applications" element={<div>Student Applications Page</div>} /> 
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<UsersPage />} />
        <Route path="/admin/employers" element={<EmployersPage />} />
        <Route path="/admin/student-report" element={<StudentReport />} />
        <Route path="/admin/employer-report" element={<EmployerReport />} />
        <Route path="/admin/full-report" element={<FullReport />} />

        
      </Routes>
    </Router>
  );
}

export default App;