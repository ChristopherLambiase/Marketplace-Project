import "./App.css";

function App() {
  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="logo">
          Market<span className="accent">place</span>
        </div>
        <nav className="nav">
          <a href="#">Home</a>
          <a href="#">Search</a>
          <a href="#">Menu</a>
        </nav>
      </header>

      {/* Table */}
      <main className="main">
        <table className="purchase-table">
          <thead>
            <tr>
              <th>Upcoming Pickup</th>
              <th>Location</th>
              <th>Time</th>
            </tr>
          </thead>
          <tbody>
            {[1, 2, 3].map((item) => (
              <tr key={item}>
                <td>
                  <div className="placeholder" />
                </td>
                <td></td>
                <td></td>
              </tr>
            ))}
          </tbody>
        </table>
      </main>
    </div>
  );
}

export default App;
