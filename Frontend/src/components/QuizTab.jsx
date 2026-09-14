import { useState, useEffect } from 'react';
import api from '../services/api';

export default function QuizTab({ projectId, onAnswered }) {
  const [attemptId, setAttemptId] = useState(null);
  const [question, setQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(null);
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);
  const [recommendation, setRecommendation] = useState(null);
  const [pastAttempts, setPastAttempts] = useState([]);
  const [checkingHistory, setCheckingHistory] = useState(true);

  const loadPastAttempts = () => {
    api.get(`/quiz/attempts/${projectId}`).then((res) => {
      setPastAttempts(res.data);
      setCheckingHistory(false);
    });
  };

  useEffect(() => {
    loadPastAttempts();
  }, [projectId]);

  const startQuiz = async () => {
    setLoading(true);
    setFeedback(null);
    setCompleted(false);
    setRecommendation(null);
    const res = await api.post('/quiz/start', { project_id: projectId });
    setAttemptId(res.data.quiz_attempt_id);
    setQuestion(res.data.question);
    setScore(null);
    setAnswer('');
    setLoading(false);
  };

  const submitAnswer = async (e) => {
    e.preventDefault();
    setLoading(true);
    const res = await api.post('/quiz/answer', {
      quiz_attempt_id: attemptId,
      question_id: question.question_id,
      answer,
    });

    setFeedback({ correct: res.data.correct, text: res.data.feedback });
    setScore(res.data.score);
    setAnswer('');
    setLoading(false);
    onAnswered();

    if (res.data.quiz_completed) {
      setCompleted(true);
      setRecommendation(res.data.recommendation);
      setQuestion(null);
      loadPastAttempts();
    } else {
      setQuestion(res.data.next_question);
    }
  };

  // Landing view: no active quiz in this session yet
  if (!attemptId) {
    if (checkingHistory) return <p>Loading quiz history...</p>;

    return (
      <div>
        <div className="text-center mb-4">
          <p>Test your understanding of this Project's concepts.</p>
          <button className="btn btn-primary" onClick={startQuiz} disabled={loading}>
            {loading ? 'Starting...' : 'Start New Quiz'}
          </button>
        </div>

        <h6>Past Quiz Attempts</h6>
        {pastAttempts.length === 0 ? (
          <p className="text-muted">No quizzes taken yet.</p>
        ) : (
          <ul className="list-group">
            {pastAttempts.map((a) => (
              <li key={a._id} className="list-group-item d-flex justify-content-between align-items-center">
                <span>
                  {new Date(a.started_at).toLocaleString()} — Score: {a.score.correct} / {a.score.total}
                </span>
                <span className={`badge ${a.status === 'completed' ? 'bg-success' : 'bg-secondary'}`}>
                  {a.status}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  return (
    <div>
      {score && <p className="text-muted">Score: {score.correct} / {score.total}</p>}

      {feedback && (
        <div className={`alert ${feedback.correct ? 'alert-success' : 'alert-warning'}`}>
          {feedback.text}
        </div>
      )}

      {completed ? (
        <div className="card p-4 text-center">
          <h4>Quiz Complete!</h4>
          <p className="mb-3">Final Score: {score.correct} / {score.total}</p>
          {recommendation && (
            <div className="alert alert-info text-start">
              <strong>Recommended next step:</strong> {recommendation}
            </div>
          )}
          <button className="btn btn-primary mt-2" onClick={startQuiz}>
            Take Another Quiz
          </button>
        </div>
      ) : (
        question && (
          <div className="card p-3 mb-3">
            <p className="small text-muted mb-1">
              {question.concept} • {question.difficulty}
            </p>
            <h5>{question.question_text}</h5>

            <form onSubmit={submitAnswer} className="mt-3">
              {question.question_type === 'multiple_choice' ? (
                <div>
                  {question.options.map((opt, i) => (
                    <div className="form-check" key={i}>
                      <input
                        className="form-check-input"
                        type="radio"
                        name="option"
                        id={`opt-${i}`}
                        value={opt}
                        checked={answer === opt}
                        onChange={(e) => setAnswer(e.target.value)}
                      />
                      <label className="form-check-label" htmlFor={`opt-${i}`}>{opt}</label>
                    </div>
                  ))}
                </div>
              ) : (
                <textarea
                  className="form-control"
                  rows="3"
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer..."
                />
              )}

              <button className="btn btn-primary mt-3" type="submit" disabled={!answer || loading}>
                {loading ? 'Submitting...' : 'Submit Answer'}
              </button>
            </form>
          </div>
        )
      )}
    </div>
  );
}