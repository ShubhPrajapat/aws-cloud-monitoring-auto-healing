function setMetric(id, barId, value) {
  const safe = Math.max(0, Math.min(100, Number(value) || 0));
  document.getElementById(id).textContent = safe.toFixed(1);
  document.getElementById(barId).style.width = safe + "%";
}
function formatUptime(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
}
async function refreshDashboard() {
  try {
    const [metricsResponse, healthResponse] = await Promise.all([
      fetch("/api/metrics", {cache:"no-store"}),
      fetch("/health", {cache:"no-store"})
    ]);
    if (!metricsResponse.ok || !healthResponse.ok) throw new Error("API request failed");
    const data = await metricsResponse.json();
    setMetric("cpu", "cpu-bar", data.cpu_percent);
    setMetric("memory", "memory-bar", data.memory_percent);
    setMetric("disk", "disk-bar", data.disk_percent);
    document.getElementById("memory-detail").textContent = `${data.memory_used_gb} GB / ${data.memory_total_gb} GB used`;
    document.getElementById("disk-detail").textContent = `${data.disk_used_gb} GB / ${data.disk_total_gb} GB used`;
    document.getElementById("hostname").textContent = data.hostname;
    document.getElementById("platform").textContent = data.platform;
    document.getElementById("uptime").textContent = formatUptime(data.uptime_seconds);
    document.getElementById("last-updated").textContent = new Date(data.timestamp).toLocaleTimeString();
    document.getElementById("overall-status").textContent = "Server operational";
    document.getElementById("app-health").textContent = "Healthy";
    document.getElementById("collector-status").textContent = "Running";
  } catch (error) {
    document.getElementById("overall-status").textContent = "Connection issue";
    document.getElementById("app-health").textContent = "Unavailable";
    document.getElementById("collector-status").textContent = "Unavailable";
  }
}
refreshDashboard();
setInterval(refreshDashboard, 10000);
