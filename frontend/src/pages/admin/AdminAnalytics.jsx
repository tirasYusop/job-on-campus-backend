import { useEffect, useState } from "react";
import axios from "axios";
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

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Tooltip,
  Legend
);

export default function AdminAnalytics() {
  const [overview, setOverview] = useState(null);
  const [trend, setTrend] = useState([]);
  const [jobTypes, setJobTypes] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [
        overviewRes,
        trendRes,
        jobTypeRes
      ] = await Promise.all([
        axios.get("http://127.0.0.1:8000/api/analytics/overview/"),
        axios.get("http://127.0.0.1:8000/api/analytics/trend/"),
        axios.get("http://127.0.0.1:8000/api/analytics/job-types/")
      ]);

      setOverview(overviewRes.data);
      setTrend(trendRes.data);
      setJobTypes(jobTypeRes.data);

    } catch (err) {
      console.error("Analytics error:", err);
    }
  };

  // ================= PIE CHART =================
  const pieData = {
    labels: overview?.status_distribution?.map(s => s.status) || [],
    datasets: [
      {
        data: overview?.status_distribution?.map(s => s.count) || []
      }
    ]
  };

  // ================= BAR TREND =================
  const barData = {
    labels: trend.map(t => t.date),
    datasets: [
      {
        label: "Applications",
        data: trend.map(t => t.count)
      }
    ]
  };

  // ================= JOB TYPE =================
  const jobTypeData = {
    labels: jobTypes.map(j => j.job_type),
    datasets: [
      {
        label: "Jobs",
        data: jobTypes.map(j => j.count)
      }
    ]
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>📊 Analytics Dashboard</h1>

      {/* ================= CARDS ================= */}
      {overview && (
        <div style={styles.cards}>
          <div style={styles.card}>
            <h3>Total Jobs</h3>
            <p>{overview.total_jobs}</p>
          </div>

          <div style={styles.card}>
            <h3>Total Applications</h3>
            <p>{overview.total_applications}</p>
          </div>
        </div>
      )}

      {/* ================= CHARTS ================= */}
      <div style={styles.charts}>

        {/* PIE */}
        <div style={styles.chartBox}>
          <h3>Status Distribution</h3>
          <Pie data={pieData} />
        </div>

        {/* BAR TREND */}
        <div style={styles.chartBox}>
          <h3>Applications Trend</h3>
          <Bar data={barData} />
        </div>

        {/* JOB TYPE */}
        <div style={styles.chartBox}>
          <h3>Job Types</h3>
          <Bar data={jobTypeData} />
        </div>

      </div>
    </div>
  );
}

// ================= SIMPLE STYLING =================
const styles = {
  container: {
    padding: "30px",
    fontFamily: "Arial"
  },
  title: {
    marginBottom: "20px"
  },
  cards: {
    display: "flex",
    gap: "20px",
    marginBottom: "30px"
  },
  card: {
    background: "#2c3e50",
    color: "white",
    padding: "20px",
    borderRadius: "10px",
    width: "200px",
    textAlign: "center"
  },
  charts: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "30px"
  },
  chartBox: {
    background: "#f4f4f4",
    padding: "20px",
    borderRadius: "10px"
  }
};