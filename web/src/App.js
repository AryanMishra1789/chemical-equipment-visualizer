import { useState, useEffect } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Backend base URL
axios.defaults.baseURL = "http://13.201.134.135:8000";
axios.defaults.withCredentials = true;
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFToken";

async function initCSRF() {
  await axios.get("/api/csrf/");
}

export default function App() {
  const [data, setData] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function init() {
      await initCSRF();
      await fetchHistory();
    }
    init();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await axios.get("/api/history/");
      setHistory(res.data);
    } catch (e) {
      console.error("Failed to fetch history", e);
    }
  };

  const uploadFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("/api/upload/", formData);
      setData(res.data);
      fetchHistory();
    } catch (err) {
      alert("Error uploading file");
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async (id, fileName) => {
    try {
      const response = await axios.get(`/api/report/${id}/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', fileName || `report-${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (e) {
      console.error("Failed to download report", e);
      alert("Failed to download report");
    }
  };

  // Helper to get status color class
  const getStatusClass = (type) => {
    const t = type.toLowerCase();
    if (t.includes("mess")) return "pump"; // Example mapping
    if (t.includes("react")) return "reactor";
    if (t.includes("tank")) return "tank";
    return "separator";
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="app-sidebar">
        <div className="logo-area">
          <div className="logo-icon">C</div>
          <div className="logo-text">ChemVis</div>
        </div>

        <ul className="nav-menu">
          <li className="nav-item active">
            <span>📊</span> Dashboard
          </li>
        </ul>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <div className="top-header">
          <h1 className="page-title">Equipment Analysis</h1>
          <p className="page-subtitle">Upload and visualize your chemical plant data</p>
        </div>

        {/* Upload Area */}
        <div className="upload-section">
          <input type="file" className="file-input" onChange={uploadFile} accept=".csv" />
          <div className="upload-icon">📂</div>
          <div className="upload-text">
            {loading ? "Processing..." : "Drag & Drop CSV File"}
          </div>
          <div className="upload-subtext">or click to browse</div>
        </div>

        {/* Report Download for current Data */}
        {data && data.id && (
          <div style={{ marginBottom: "2rem", textAlign: "right" }}>
            <button
              onClick={() => downloadReport(data.id, "current-report.pdf")}
              style={{
                background: "#0ea5e9", color: "white", padding: "10px 20px",
                border: "none", borderRadius: "6px", cursor: "pointer", fontSize: "1rem"
              }}
            >
              📥 Download PDF Report
            </button>
          </div>
        )}

        {data ? (
          <div className="dashboard-grid">

            <div className="right-panel" style={{ gridColumn: '1 / -1' }}>
              {/* Stats Row */}
              <div className="stats-container">
                <StatCard title="Total Equipment" value={data.total_equipment} trend="+12%" />
                <StatCard title="Avg Flowrate" value={data.avg_flowrate.toFixed(2)} unit="m³/h" />
                <StatCard title="Avg Pressure" value={data.avg_pressure.toFixed(2)} unit="bar" />
                <StatCard title="Avg Temperature" value={data.avg_temperature.toFixed(2)} unit="°C" />
              </div>

              {/* Download Report Button */}
              {data.id && (
                <div style={{ marginBottom: '1rem' }}>
                  <button
                    onClick={() => downloadReport(data.id, 'equipment_report.pdf')}
                    style={{
                      background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
                      color: 'white',
                      border: 'none',
                      padding: '12px 28px',
                      borderRadius: '8px',
                      fontSize: '15px',
                      fontWeight: 'bold',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    📥 Download PDF Report
                  </button>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
                {/* Chart Section */}
                <div className="chart-card">
                  <h3>Equipment Distribution</h3>
                  <div style={{ height: '300px', display: 'flex', justifyContent: 'center' }}>
                    <Bar
                      data={{
                        labels: Object.keys(data.type_distribution),
                        datasets: [{
                          label: "Count",
                          data: Object.values(data.type_distribution),
                          backgroundColor: ['#0ea5e9', '#6366f1', '#22c55e', '#f43f5e'],
                          borderRadius: 6,
                        }]
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { display: false }
                        },
                        scales: {
                          y: { grid: { color: '#e2e8f0' } },
                          x: { grid: { display: false } }
                        }
                      }}
                    />
                  </div>
                </div>

                {/* Recent History Sidebar (Moved here for layout) */}
                <div className="history-card">
                  <div className="card-header">Video Recent Uploads</div>
                  <ul className="history-list">
                    {history.slice(0, 5).map(item => (
                      <li key={item.id} className="history-item">
                        <div className="file-icon">📄</div>
                        <div className="file-info">
                          <span className="file-name">{item.name}</span>
                          <span className="file-meta">{item.total} items • {new Date(item.uploaded_at).toLocaleDateString()}</span>
                        </div>
                        <button
                          onClick={() => downloadReport(item.id, `report-${item.name}.pdf`)}
                          title="Download PDF"
                          style={{
                            background: "transparent", border: "1px solid #e2e8f0",
                            borderRadius: "4px", cursor: "pointer", padding: "4px 8px"
                          }}
                        >
                          ⬇️
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>


              {/* Data Table */}
              <div className="table-card">
                <div className="card-header" style={{ padding: '1.5rem' }}>Detailed Equipment Data</div>
                <div className="table-wrapper">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th>Equipment Name</th>
                        <th>Type</th>
                        <th>Flowrate</th>
                        <th>Pressure</th>
                        <th>Temperature</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.table.map((row, i) => (
                        <tr key={i}>
                          <td><b>{row["Equipment Name"]}</b></td>
                          <td>{row.Type}</td>
                          <td>{row.Flowrate}</td>
                          <td>{row.Pressure}</td>
                          <td>{row.Temperature}</td>
                          <td>
                            <span className={`status-badge ${getStatusClass(row.Type)}`}>
                              Active
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

          </div>
        ) : (
          <div className="empty-state">
            <div className="history-card">
              <div className="card-header">Recent Uploads</div>
              <ul className="history-list">
                {history.map(item => (
                  <li key={item.id} className="history-item">
                    <div className="file-icon">📄</div>
                    <div className="file-info">
                      <span className="file-name">{item.name}</span>
                      <span className="file-meta">
                        {item.total} equipment items found • {new Date(item.uploaded_at).toLocaleDateString()}
                      </span>
                    </div>
                    <button
                      onClick={() => downloadReport(item.id, `report-${item.name}.pdf`)}
                      title="Download PDF"
                      style={{
                        background: "transparent", border: "1px solid #e2e8f0",
                        borderRadius: "4px", cursor: "pointer", padding: "4px 8px"
                      }}
                    >
                      ⬇️
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

function StatCard({ title, value, unit, trend }) {
  return (
    <div className="stat-card">
      <div className="stat-title">{title}</div>
      <div className="stat-value">
        {value} <span style={{ fontSize: '0.5em', color: '#94a3b8' }}>{unit}</span>
      </div>
      {trend && <div className="stat-trend">{trend} from last month</div>}
    </div>
  );
}

