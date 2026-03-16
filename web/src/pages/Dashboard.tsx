import React, { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

type PortfolioState = {
  equity: number;
  day_pnl: number;
  leverage: number;
};

type DemoResponse = {
  executed_orders: number;
  state: PortfolioState;
};

type EquityPoint = { t: number; equity: number };

type RiskSnapshot = {
  equity: number;
  day_pnl: number;
  max_daily_loss: number;
  max_leverage: number;
  current_leverage: number;
};

export const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<string | null>(null);
  const [demo, setDemo] = useState<DemoResponse | null>(null);
  const [equityCurve, setEquityCurve] = useState<EquityPoint[]>([]);
  const [risk, setRisk] = useState<RiskSnapshot | null>(null);
  const [stream, setStream] = useState<EquityPoint[]>([]);
  const [error, setError] = useState<string | null>(null);

  const checkHealth = async () => {
    setError(null);
    try {
      const res = await fetch("/api/health");
      const data = await res.json();
      setHealth(data.status);
    } catch (e: any) {
      setError(String(e));
    }
  };

  const runDemo = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/demo/run", { method: "POST" });
      const data = await res.json();
      setDemo(data);
    } catch (e: any) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const loadEquityCurve = async () => {
    setError(null);
    try {
      const res = await fetch("/api/equity_curve");
      const data = await res.json();
      setEquityCurve(data);
    } catch (e: any) {
      setError(String(e));
    }
  };

  const loadRisk = async () => {
    setError(null);
    try {
      const res = await fetch("/api/risk");
      const data = await res.json();
      setRisk(data);
    } catch (e: any) {
      setError(String(e));
    }
  };

  const startStream = () => {
    setStream([]);
    setError(null);
    const ws = new WebSocket("ws://localhost:5173/ws/stream");
    ws.onmessage = (evt) => {
      const msg = JSON.parse(evt.data);
      setStream((prev) => [
        ...prev,
        { t: prev.length, equity: msg.equity as number }
      ]);
    };
    ws.onerror = (e) => {
      setError(String(e));
    };
  };

  useEffect(() => {
    // initial load
    loadRisk();
  }, []);

  return (
    <main style={{ maxWidth: 1200, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
      <h1>Ultimate AI Trading Platform v4</h1>
      <p>FastAPI + React 기반 트레이딩 대시보드 (전략/리스크/Equity 모니터링).</p>

      <section style={{ marginTop: 24, display: "flex", gap: 24 }}>
        <div>
          <h2>API Health</h2>
          <button onClick={checkHealth}>Check API</button>
          {health && <p>API status: {health}</p>}
        </div>

        <div>
          <h2>Run Demo Step</h2>
          <button onClick={runDemo} disabled={loading}>
            {loading ? "Running..." : "Run Demo"}
          </button>
          {demo && (
            <div style={{ marginTop: 12 }}>
              <p>Executed orders: {demo.executed_orders}</p>
              <p>Equity: {demo.state.equity}</p>
              <p>Day PnL: {demo.state.day_pnl}</p>
              <p>Leverage: {demo.state.leverage}</p>
            </div>
          )}
        </div>

        <div>
          <h2>Risk Snapshot</h2>
          <button onClick={loadRisk}>Refresh Risk</button>
          {risk && (
            <table style={{ marginTop: 8, borderCollapse: "collapse" }}>
              <tbody>
                <tr>
                  <td>Equity</td>
                  <td style={{ paddingLeft: 8 }}>{risk.equity}</td>
                </tr>
                <tr>
                  <td>Day PnL</td>
                  <td style={{ paddingLeft: 8 }}>{risk.day_pnl}</td>
                </tr>
                <tr>
                  <td>Max Daily Loss</td>
                  <td style={{ paddingLeft: 8 }}>{risk.max_daily_loss}</td>
                </tr>
                <tr>
                  <td>Leverage</td>
                  <td style={{ paddingLeft: 8 }}>
                    {risk.current_leverage} / {risk.max_leverage}
                  </td>
                </tr>
              </tbody>
            </table>
          )}
        </div>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Equity Curve (Sample)</h2>
        <button onClick={loadEquityCurve}>Load Equity Curve</button>
        <div style={{ width: "100%", height: 240, marginTop: 12 }}>
          <ResponsiveContainer>
            <LineChart data={equityCurve}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="t" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="equity" stroke="#3b82f6" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section style={{ marginTop: 32 }}>
        <h2>Live Stream (WebSocket, Equity)</h2>
        <button onClick={startStream}>Start Stream</button>
        <div style={{ width: "100%", height: 240, marginTop: 12 }}>
          <ResponsiveContainer>
            <LineChart data={stream}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="t" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="equity" stroke="#10b981" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      {error && (
        <section style={{ marginTop: 24, color: "red" }}>
          <h3>Error</h3>
          <pre>{error}</pre>
        </section>
      )}
    </main>
  );
};

