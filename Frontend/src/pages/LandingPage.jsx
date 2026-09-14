import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div>
      {/* Nav bar */}
      <nav className="navbar navbar-dark bg-dark px-4">
        <span className="navbar-brand mb-0 h1">AI Study Companion</span>
        <div>
          <Link to="/login" className="btn btn-outline-light btn-sm me-2">Log In</Link>
          <Link to="/signup" className="btn btn-light btn-sm">Sign Up</Link>
        </div>
      </nav>

      {/* Hero section */}
      <div className="container text-center py-5">
        <h1 className="display-5 fw-bold mb-3">Learn smarter, not just harder.</h1>
        <p className="lead text-muted mb-4">
          Upload your study material, ask an AI tutor grounded in your own notes,
          test yourself with adaptive quizzes, and track your growth over time.
        </p>
        <Link to="/signup" className="btn btn-primary btn-lg me-2">Get Started</Link>
        <Link to="/login" className="btn btn-outline-secondary btn-lg">Log In</Link>
      </div>

      {/* Feature highlights */}
      <div className="container py-4">
        <div className="row g-4">
          <div className="col-md-4">
            <div className="card h-100 p-3">
              <h5>📚 Grounded AI Tutor</h5>
              <p className="text-muted mb-0">
                Ask questions and get answers backed by your own uploaded materials,
                with page-level citations — never a guess.
              </p>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 p-3">
              <h5>🎯 Adaptive Quizzes</h5>
              <p className="text-muted mb-0">
                Questions adjust to your current understanding, focusing on the
                concepts you actually need to work on.
              </p>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card h-100 p-3">
              <h5>📈 Growth Tracking</h5>
              <p className="text-muted mb-0">
                See your mastery evolve over time, concept by concept, with
                clear recommendations on what to study next.
              </p>
            </div>
          </div>
        </div>
      </div>

      <footer className="text-center text-muted py-4 mt-3 small">
        AI Study Companion — a learning workspace prototype.
        <br />
        <Link to="/admin/login" className="text-muted">Admin Portal</Link>
      </footer>
    </div>
  );
}