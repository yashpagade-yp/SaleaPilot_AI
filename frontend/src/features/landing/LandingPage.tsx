import { Link } from "react-router-dom";

const personaCards = [
  {
    title: "Ideal buyer",
    text: "Practice a strong consultative conversation with a buyer who is engaged, attentive, and ready to explore value.",
  },
  {
    title: "Busy buyer",
    text: "Sharpen shorter pitches and earn attention quickly when time is limited and interruptions happen early.",
  },
  {
    title: "Rude buyer",
    text: "Build resilience, composure, and control when objections come with frustration or abrupt pushback.",
  },
];

const workflowSteps = [
  {
    title: "Admin unlocks access",
    text: "The journey starts with controlled access and a real invitation sent to the salesperson email.",
  },
  {
    title: "Salesperson accepts the invite",
    text: "The invite link opens the acceptance step with the email and invitation code already in place.",
  },
  {
    title: "AI practice begins",
    text: "The salesperson selects a persona and enters a focused voice practice experience inside the workspace.",
  },
  {
    title: "Conversation gets stored",
    text: "The session can be synced back into the product for transcript review and call-by-call visibility.",
  },
  {
    title: "Feedback closes the loop",
    text: "Coaching feedback turns each session into concrete next-step improvement instead of one-off calling.",
  },
];

export function LandingPage() {
  return (
    <main className="landing-page">
      <section className="hero-section section-shell">
        <div className="hero-badge">Sales rehearsal for modern teams</div>
        <h1 className="hero-title">
          Build sharper sales calls <span>before the real customer ever joins.</span>
        </h1>
        <p className="hero-copy">
          SalesPilot AI gives your team a dark, focused practice workspace for live AI roleplay,
          conversation review, and coaching feedback that closes the loop.
        </p>
        <div className="hero-actions">
          <Link className="button button-primary" to="/login">
            Start product access
          </Link>
          <a className="button button-secondary" href="#product-flow">
            Explore the workflow
          </a>
        </div>
        <div className="hero-panel">
          <div className="hero-panel-chip">Voice-ready practice</div>
          <div className="hero-panel-grid">
            <article className="hero-metric">
              <strong>Admin-led access</strong>
              <span>Invite and control who enters the coaching workspace.</span>
            </article>
            <article className="hero-metric">
              <strong>AI persona calls</strong>
              <span>Run realistic sessions with ideal, busy, and rude customers.</span>
            </article>
            <article className="hero-metric">
              <strong>Transcript + feedback</strong>
              <span>Review what happened and where the salesperson should improve.</span>
            </article>
          </div>
        </div>
      </section>

      <section id="product-flow" className="section-shell story-section">
        <div className="section-heading">
          <span className="eyebrow">How the product moves</span>
          <h2>One journey, from admin access to salesperson improvement.</h2>
          <p>
            The flow starts with admin control and ends with a salesperson reviewing practice,
            conversation history, and coaching feedback in one product system.
          </p>
        </div>
        <div className="timeline-grid">
          {workflowSteps.map((step) => (
            <article key={step.title} className="timeline-card">
              <strong>{step.title}</strong>
              <p>{step.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section-shell personas-section">
        <div className="section-heading">
          <span className="eyebrow">Practice personas</span>
          <h2>Train for the customer energy your reps actually face.</h2>
          <p>
            SalesPilot AI is not just a call launcher. It is a rehearsal system built around clear
            persona pressure, controlled repetition, and fast feedback.
          </p>
        </div>
        <div className="persona-grid">
          {personaCards.map((persona) => (
            <article key={persona.title} className="persona-card">
              <div className="persona-orb" />
              <h3>{persona.title}</h3>
              <p>{persona.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="section-shell review-section">
        <div className="section-heading">
          <span className="eyebrow">After the session</span>
          <h2>Conversation history and feedback stay central to the product.</h2>
          <p>
            The workspace is built around three connected areas: agents, conversations, and
            feedback. Practice is only useful when the salesperson can return, review, and improve.
          </p>
        </div>
        <div className="review-grid">
          <article className="review-card">
            <strong>Agents</strong>
            <p>Choose the right persona, review the challenge, and start the next voice session.</p>
          </article>
          <article className="review-card">
            <strong>Conversations</strong>
            <p>Open transcripts, inspect session history, and track how each practice call evolved.</p>
          </article>
          <article className="review-card">
            <strong>Feedback</strong>
            <p>See strengths, improvement areas, scores, and practical recommendations after every session.</p>
          </article>
        </div>
      </section>

      <section className="section-shell cta-section">
        <div className="cta-card">
          <div>
            <span className="eyebrow">Unified product entry</span>
            <h2>One login entry. Role-based routing. Focused workspaces.</h2>
            <p>
              Admins move into access management. Invited salespeople continue into AI practice,
              conversation review, and performance feedback.
            </p>
          </div>
          <div className="cta-actions">
            <Link className="button button-primary" to="/login">
              Enter SalesPilot AI
            </Link>
            <Link className="button button-secondary" to="/accept-invitation">
              Accept invitation
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
