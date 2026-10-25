
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/analyze";
const HISTORY_URL = "http://127.0.0.1:8000/api/history";

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [activeView, setActiveView] = useState("analyze");
  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");

  function handleResumeChange(event) {
    const file = event.target.files?.[0] ?? null;

    setMessage("");
    setResults(null);

    if (!file) {
      setResume(null);
      return;
    }

    if (
      !file.name.toLowerCase().endsWith(".pdf") ||
      (file.type && file.type !== "application/pdf")
    ) {
      setResume(null);
      event.target.value = "";
      setMessage("Please select a valid PDF resume.");
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setResume(null);
      event.target.value = "";
      setMessage("Your PDF must be 5 MB or smaller.");
      return;
    }

    setResume(file);
  }

  async function handleAnalyze() {
    if (loading) return;

    if (!resume) {
      setMessage("Please upload your resume PDF first.");
      return;
    }

    if (!jobDescription.trim()) {
      setMessage("Please paste a job description.");
      return;
    }

    setLoading(true);
    setMessage("");
    setResults(null);

    try {
      const formData = new FormData();
      formData.append("resume", resume);
      formData.append("job_description", jobDescription.trim());

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail = data.detail;

        const errorMessage = Array.isArray(detail)
          ? detail.map((item) => item.msg).join(", ")
          : detail || `Request failed with status ${response.status}.`;

        throw new Error(errorMessage);
      }

      setResults(data);
      setMessage("Your resume analysis is complete.");
    } catch (error) {
      setMessage(
        error.message ||
          "Could not connect to the backend. Make sure FastAPI is running."
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadHistory() {
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const response = await fetch(HISTORY_URL);

      if (!response.ok) {
        throw new Error("Could not load analysis history.");
      }

      const data = await response.json();
      setHistory(Array.isArray(data) ? data : []);
    } catch (error) {
      setHistoryError(
        error.message || "Could not connect to the backend."
      );
    } finally {
      setHistoryLoading(false);
    }
  }

  function resetForm() {
    setResume(null);
    setJobDescription("");
    setMessage("");
    setResults(null);

    const fileInput = document.getElementById("resume-upload");
    if (fileInput) fileInput.value = "";
  }


  const importanceBreakdown = ["Required", "Preferred", "Standard"].map(
    (level) => {
      const skills = Object.entries(results?.skill_importance ?? {})
        .filter(([, importance]) => importance === level)
        .map(([skill]) => skill);

      const matchedSkills = results?.matched_skills ?? [];

      return {
        level,
        total: skills.length,
        matched: skills.filter((skill) =>
          matchedSkills.includes(skill)
        ).length,
      };
    }
  );


  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/">
          <span className="brand-icon">C</span>
          CareerMatch <span className="brand-ai">AI</span>
        </a>

        <span className="topbar-label">Resume Intelligence</span>

        <nav className="topbar-nav" aria-label="Main navigation">
          <button
            type="button"
            className={activeView === "analyze" ? "nav-button active" : "nav-button"}
            onClick={() => setActiveView("analyze")}
          >
            Analyze Resume
          </button>

          <button
            type="button"
            className={activeView === "history" ? "nav-button active" : "nav-button"}
            onClick={() => {
              setActiveView("history");
              loadHistory();
            }}
          >
            History
          </button>
        </nav>
      </header>

      <main className="main-content">
        <section className="hero">
          <span className="eyebrow">YOUR NEXT CAREER MOVE</span>

          <h1>
            Make your resume
            <br />
            <span>work for you.</span>
          </h1>

          <p>
            Compare your resume with a job description, discover
            skill gaps, and prepare for your next opportunity.
          </p>
        </section>

      {activeView === "analyze" ? (
        <section className="workspace">
          <div className="panel">
            <div className="panel-heading">
              <span className="step-number">01</span>
              <div>
                <h2>Upload your resume</h2>
                <p>Choose your latest resume in PDF format.</p>
              </div>
            </div>

            <label className="upload-area" htmlFor="resume-upload">
              <span className="upload-icon">↑</span>

              <strong>
                {resume ? resume.name : "Choose your resume"}
              </strong>

              <span>
                {resume
                  ? `${(resume.size / 1024).toFixed(1)} KB · PDF selected`
                  : "Click here to browse PDF files · Max 5 MB"}
              </span>

              <input
                id="resume-upload"
                type="file"
                accept=".pdf,application/pdf"
                onChange={handleResumeChange}
                disabled={loading}
              />
            </label>
          </div>

          <div className="panel">
            <div className="panel-heading">
              <span className="step-number">02</span>
              <div>
                <h2>Add the job description</h2>
                <p>
                  Paste the job requirements for the role you want.
                </p>
              </div>
            </div>

            <textarea
              className="job-input"
              value={jobDescription}
              onChange={(event) => {
                setJobDescription(event.target.value);
                setMessage("");
                setResults(null);
              }}
              placeholder={`Paste the job description here...

Example:
Required skills: Python, SQL, React, FastAPI
Responsibilities: Develop APIs, work with databases, and build web applications.`}
              disabled={loading}
            />

            <div className="input-footer">
              <span>{jobDescription.length} characters</span>
              <span>Job description</span>
            </div>
          </div>

          <button
            className="analyze-button"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Analyzing resume..." : "Analyze my resume"}
            {!loading && <span> →</span>}
          </button>

          {message && (
            <p
              className="feedback"
              role="status"
              aria-live="polite"
            >
              {message}
            </p>
          )}

          {results && (
            <section className="panel results-panel">
              <div className="panel-heading">
                <span className="step-number">03</span>
                <div>
                  <h2>Analysis Results</h2>
                  <p>
                    Results for {results.filename || resume?.name}
                  </p>
                </div>
              </div>


              <div className="score-section">
                <span className="score-label">Skill match score</span>

                <div className="score-value">
                  {results.match_score}%
                </div>

                <div
                  className="score-track"
                  role="progressbar"
                  aria-label="Skill match score"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={results.match_score}
                >
                  <div
                    className="score-fill"
                    style={{
                      width: `${Math.min(
                        100,
                        Math.max(0, results.match_score)
                      )}%`,
                    }}
                  />
                </div>

                <p>
                  {results.job_skills?.length
                    ? `${results.matched_skills.length} of ${results.job_skills.length} recognized job skills found in your resume.`
                    : "No recognized skills were found in the job description."}
                </p>

                {results.score_available && (
                  <p className="score-method-note">
                    Scoring method: {results.score_method || "Weighted skill coverage"}.
                    Matched skill weight: {results.matched_skill_weight} of{" "}
                    {results.total_skill_weight}.
                  </p>
                )}

                <div className="importance-breakdown">
                  <h3>Skill importance breakdown</h3>

                  <p className="breakdown-description">
                    See how your resume matches the different skill priorities
                    identified in the job description.
                  </p>

                  <div className="importance-grid">
                    {importanceBreakdown.map((item) => (
                      <div className="importance-card" key={item.level}>
                        <span className={`importance-label ${item.level.toLowerCase()}`}>
                          {item.level}
                        </span>

                        <div className="importance-count">
                          {item.matched}
                          <span> / {item.total}</span>
                        </div>

                        <p>skills matched</p>
                      </div>
                    ))}
                  </div>

                  <p className="breakdown-footnote">
                    Required skills receive higher weight than preferred skills.
                    Standard skills use the default weight. These categories are
                    estimated from job-description wording.
                  </p>
                </div>
              </div>


              <div className="skills-results">
                <div className="skill-group">
                  <h3>Matched skills</h3>
                  {results.matched_skills?.length ? (
                    <div className="skill-list">
                      {results.matched_skills.map((skill) => (
                        <span className="skill-tag matched" key={skill}>
                          ✓ {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="empty-state">No matching skills found.</p>
                  )}
                </div>

                <div className="skill-group">
                  <h3>Skills to develop</h3>
                  {results.missing_skills?.length ? (
                    <div className="skill-list">
                      {results.missing_skills.map((skill) => (
                        <span className="skill-tag missing" key={skill}>
                          + {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="empty-state">
                      No missing recognized skills.
                    </p>
                  )}
                </div>

                <div className="skill-group">
                  <h3>Skills detected in your resume</h3>
                  {results.resume_skills?.length ? (
                    <div className="skill-list">
                      {results.resume_skills.map((skill) => (
                        <span className="skill-tag" key={skill}>
                          {skill}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="empty-state">
                      No recognized skills detected.
                    </p>
                  )}
                </div>
              </div>


                <div className="skill-breakdowns">
                  {[
                    {
                      title: "Resume Skill Categories",
                      breakdown: results.resume_skill_breakdown,
                    },
                    {
                      title: "Job Skill Categories",
                      breakdown: results.job_skill_breakdown,
                    },
                  ].map(({ title, breakdown }) => (
                    <section
                      className="skill-breakdown-section"
                      key={title}
                    >
                      <h3>{title}</h3>

                      {breakdown &&
                      Object.keys(breakdown).length > 0 ? (
                        <div className="skill-category-grid">
                          {Object.entries(breakdown).map(
                            ([category, details]) => (
                              <article
                                className="skill-category-card"
                                key={category}
                              >
                                <div className="skill-category-heading">
                                  <h4>{category}</h4>

                                  <span>
                                    {details.count ??
                                      details.skills?.length ??
                                      0}{" "}
                                    skills
                                  </span>
                                </div>

                                <div className="skill-list">
                                  {(details.skills ?? []).map(
                                    (skill) => (
                                      <span
                                        className="skill-tag"
                                        key={skill}
                                      >
                                        {skill}
                                      </span>
                                    )
                                  )}
                                </div>
                              </article>
                            )
                          )}
                        </div>
                      ) : (
                        <p className="empty-state">
                          No skill categories available.
                        </p>
                      )}
                    </section>
                  ))}
                </div>


                {results.ai_feedback && (
                  <section className="ai-feedback-section">
                    <div className="recommendations-heading">
                      <span className="recommendations-icon">✦</span>
                      <div>
                        <h3>AI Resume Feedback</h3>
                        <p>
                          Personalized feedback based on your resume
                          and the job description.
                        </p>
                      </div>
                    </div>

                    <div className="ai-feedback-overall">
                      <h4>Overall Feedback</h4>
                      <p>
                        {results.ai_feedback.overall_feedback ||
                          "No overall feedback available."}
                      </p>
                    </div>

                    {[
                      {
                        title: "Strengths",
                        items: results.ai_feedback.strengths,
                      },
                      {
                        title: "Areas for Improvement",
                        items: results.ai_feedback.improvements,
                      },
                      {
                        title: "Resume Tips",
                        items: results.ai_feedback.resume_tips,
                      },
                    ].map(({ title, items }) => (
                      <div className="ai-feedback-card" key={title}>
                        <h4>{title}</h4>

                        {Array.isArray(items) && items.length > 0 ? (
                          <ul>
                            {items.map((item, index) => (
                              <li key={`${title}-${index}`}>{item}</li>
                            ))}
                          </ul>
                        ) : (
                          <p>No items available.</p>
                        )}
                      </div>
                    ))}
                  </section>
                )}

                {results.recommendations?.length > 0 && (
                  <div className="recommendations-section">
                    <div className="recommendations-heading">
                      <span className="recommendations-icon">✦</span>
                      <div>
                        <h3>Improve your resume match</h3>
                        <p>
                          Practical next steps based on the skills
                          identified in this job description.
                        </p>
                      </div>
                    </div>

                    <div className="recommendations-list">
                      {results.recommendations.map((item) => (
                        <article
                          className="recommendation-card"
                          key={item.skill}
                        >
                          <span className="recommendation-skill">
                            {item.skill}
                          </span>

                          <div className="recommendation-detail">
                            <h4>Why this skill was flagged</h4>
                            <p>{item.reason}</p>
                          </div>

                          <div className="recommendation-detail">
                            <h4>What to learn</h4>
                            <p>{item.suggestion}</p>
                          </div>

                          <div className="recommendation-detail">
                            <h4>Project idea</h4>
                            <p>{item.project_idea}</p>
                          </div>
                        </article>
                      ))}
                    </div>
                  </div>
                )}

              <p className="results-note">
                This score reflects recognized keyword matches, not
                your overall employability. A missing keyword does
                not necessarily mean you lack that skill.
              </p>

              <button
                type="button"
                className="reset-button"
                onClick={resetForm}
              >
                Analyze another resume
              </button>
            </section>
          )}
        </section>
        ) : (
          <section className="panel history-panel">
            <div className="panel-heading">
              <span className="step-number">04</span>
              <div>
                <h2>Analysis History</h2>
                <p>Review resumes you've analyzed previously.</p>
              </div>
            </div>

            {historyLoading && <p>Loading your analysis history...</p>}

            {historyError && (
              <p className="feedback" role="alert">{historyError}</p>
            )}

            {!historyLoading && !historyError && history.length === 0 && (
              <p className="empty-state">
                No saved analyses found. Analyze a resume to see it here.
              </p>
            )}

            {!historyLoading && history.length > 0 && (
              <div className="history-list">
                {history.map((item) => (
                  <article className="history-card" key={item.id}>
              <div>
                <h3>{item.filename}</h3>
                <p>
                  {item.created_at
                    ? new Date(item.created_at).toLocaleString()
                    : "Date unavailable"}
                </p>
              </div>

              <div className="history-score">
                {item.match_score}%
                <span>Match score</span>
              </div>

              <details>
                <summary>View job description</summary>
                <p className="history-description">
                  {item.job_description}
                </p>
              </details>
            </article>
          ))}
        </div>
      )}

      <button
        type="button"
        className="reset-button"
        onClick={loadHistory}
        disabled={historyLoading}
      >
        Refresh History
      </button>
    </section>
  )}

        <footer className="footer">
          CareerMatch AI · Built to help you prepare for your next role.
        </footer>
      </main>
    </div>
  );
}

export default App;
