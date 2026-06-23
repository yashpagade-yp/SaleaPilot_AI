import { Button } from "../../components/ui/button";
import { Card } from "../../components/ui/card";
import { SectionTitle } from "../../components/ui/section-title";
import { StatusPill } from "../../components/ui/status-pill";

const landingSlides = [
  {
    id: "hero",
    eyebrow: "Slide 1",
    title: "Train every sales call before it happens.",
    description:
      "SalesPilot AI gives your team a dark, voice-first rehearsal space where realistic personas push back, interrupt, challenge, and help reps sharpen the moments that matter.",
  },
  {
    id: "personas",
    eyebrow: "Slide 2",
    title: "Switch between real objection styles in seconds.",
    description:
      "Practice against ideal, rude, and busy personas without rebuilding the workflow. Each scenario is built to make reps handle pressure, context changes, and conversation control.",
  },
  {
    id: "calling",
    eyebrow: "Slide 3",
    title: "Join browser calls with a voice-native experience.",
    description:
      "Built around live practice, not passive learning. Reps can start a session, enter the call quickly, and stay focused on the conversation itself.",
  },
  {
    id: "feedback",
    eyebrow: "Slide 4",
    title: "Review transcript, session history, and coaching signals.",
    description:
      "After every training call, the workspace surfaces transcript context, conversation sync status, and feedback summaries so reps know what to improve next.",
  },
  {
    id: "cta",
    eyebrow: "Slide 5",
    title: "Bring every training moment into one polished experience.",
    description:
      "From first impression to daily use, SalesPilot AI keeps team setup, call practice, and coaching in one focused product experience.",
  },
];

const slideAnchors = [
  { href: "#hero", label: "Hero" },
  { href: "#personas", label: "Personas" },
  { href: "#calling", label: "Calling flow" },
  { href: "#feedback", label: "Feedback loop" },
  { href: "#cta", label: "Launch" },
];

const personaCards = [
  {
    title: "Ideal customer",
    summary: "Warm and open. Great for discovery structure and confidence building.",
    tone: "success" as const,
  },
  {
    title: "Rude customer",
    summary: "Pushes emotional control, objection handling, and composure under pressure.",
    tone: "warning" as const,
  },
  {
    title: "Busy customer",
    summary: "Forces brevity, fast value framing, and clearer meeting conversion.",
    tone: "neutral" as const,
  },
];

const workflowSteps = [
  "A team lead signs in and invites the salesperson by email.",
  "The salesperson opens their invite and signs in with a one-time code.",
  "Rep chooses a fixed training persona and starts the session.",
  "The rep joins the live practice call and handles the conversation in real time.",
  "History, transcript, and coaching feedback stay connected to the same flow.",
];

export function LandingPage() {
  return (
    <div style={{ paddingBottom: 72 }}>
      <header
        style={{
          position: "sticky",
          top: 0,
          zIndex: 10,
          backdropFilter: "blur(18px)",
          background: "rgba(5, 10, 19, 0.68)",
          borderBottom: "1px solid rgba(123, 163, 255, 0.12)",
        }}
      >
        <div
          className="page-shell"
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
            padding: "18px 0",
          }}
        >
          <div style={{ display: "grid", gap: 4 }}>
            <strong style={{ fontSize: "1.1rem" }}>SalesPilot AI</strong>
            <span style={{ color: "#9eb0cf", fontSize: "0.92rem" }}>
              Voice-first practice for sales calls
            </span>
          </div>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap", alignItems: "center" }}>
            <nav style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
              {slideAnchors.map((slide) => (
                <a
                  key={slide.href}
                  href={slide.href}
                  style={{
                    color: "#9eb0cf",
                    fontSize: "0.95rem",
                    padding: "8px 0",
                  }}
                >
                  {slide.label}
                </a>
              ))}
            </nav>
            <Button variant="ghost" to="/admin">
              Admin
            </Button>
            <Button variant="secondary" to="/workspace">
              Workspace
            </Button>
          </div>
        </div>
      </header>

      <main style={{ display: "grid", gap: 96 }}>
        <section className="page-shell" id="hero" style={{ paddingTop: 56 }}>
          <div
            className="panel grid-glow hero-grid"
            style={{
              padding: "44px clamp(24px, 4vw, 56px)",
            }}
          >
            <div style={{ display: "grid", gap: 22 }}>
              <span className="section-label">AI Web Calling Bot</span>
              <h1
                style={{
                  margin: 0,
                  fontSize: "clamp(3rem, 7vw, 5.8rem)",
                  lineHeight: 0.98,
                  letterSpacing: "-0.04em",
                }}
              >
                Dark, focused training for real sales conversations.
              </h1>
              <p
                style={{
                  margin: 0,
                  maxWidth: 640,
                  color: "#9eb0cf",
                  fontSize: "1.08rem",
                  lineHeight: 1.8,
                }}
              >
                Build confidence in live customer calls through realistic AI personas, browser-based voice sessions, and post-call coaching that keeps the feedback loop clear.
              </p>
              <div style={{ display: "flex", gap: 14, flexWrap: "wrap" }}>
                <Button to="/workspace">Start salesperson flow</Button>
                <Button variant="secondary" to="/admin">
                  Admin login
                </Button>
              </div>
              <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
                <StatusPill label="Web calling" />
                <StatusPill label="Scenario-led practice" />
                <StatusPill label="Transcript + coaching" />
              </div>
            </div>

            <Card
              style={{
                display: "grid",
                gap: 18,
                alignSelf: "stretch",
                background:
                  "linear-gradient(180deg, rgba(12, 22, 39, 0.96) 0%, rgba(8, 15, 27, 0.98) 100%)",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <strong>Live call pulse</strong>
                <StatusPill label="Ready to join" tone="success" />
              </div>
              <div
                style={{
                  display: "grid",
                  gap: 16,
                  padding: 18,
                  borderRadius: 20,
                  background: "rgba(6, 16, 30, 0.72)",
                  border: "1px solid rgba(123, 163, 255, 0.12)",
                }}
              >
                <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                  <div
                    style={{
                      width: 12,
                      height: 12,
                      borderRadius: 999,
                      background: "#3dd6a0",
                      boxShadow: "0 0 0 8px rgba(61, 214, 160, 0.1)",
                    }}
                  />
                  <span style={{ color: "#9eb0cf" }}>Daily room connected</span>
                </div>
                <div
                  style={{
                    height: 120,
                    borderRadius: 18,
                    background:
                      "linear-gradient(180deg, rgba(104, 213, 255, 0.12), rgba(139, 124, 255, 0.08))",
                    border: "1px solid rgba(123, 163, 255, 0.16)",
                    position: "relative",
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      inset: "auto 12px 18px",
                      height: 38,
                      borderRadius: 999,
                      background:
                        "repeating-linear-gradient(90deg, rgba(104, 213, 255, 0.9) 0 6px, transparent 6px 14px)",
                      opacity: 0.8,
                    }}
                  />
                </div>
                <div style={{ display: "grid", gap: 8 }}>
                  <div style={{ color: "#eff4ff", fontWeight: 700 }}>Current persona: Busy customer</div>
                  <div style={{ color: "#9eb0cf" }}>
                    Goal: deliver a shorter pitch, earn attention quickly, and handle interruption without losing clarity.
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </section>

        <section className="page-shell" id="personas" style={{ display: "grid", gap: 28 }}>
          <SectionTitle
            eyebrow={landingSlides[1].eyebrow}
            title={landingSlides[1].title}
            description={landingSlides[1].description}
          />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 18,
            }}
          >
            {personaCards.map((card) => (
              <Card key={card.title} style={{ display: "grid", gap: 14 }}>
                <StatusPill label={card.title} tone={card.tone} />
                <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
                  {card.summary}
                </p>
              </Card>
            ))}
          </div>
        </section>

        <section className="page-shell" id="calling" style={{ display: "grid", gap: 28 }}>
          <SectionTitle
            eyebrow={landingSlides[2].eyebrow}
            title={landingSlides[2].title}
            description={landingSlides[2].description}
          />
          <div
            className="panel"
            style={{
              padding: 28,
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: 20,
            }}
          >
            <Card style={{ background: "rgba(6, 16, 30, 0.72)" }}>
              <div style={{ display: "grid", gap: 14 }}>
                <strong>Calling flow</strong>
                {workflowSteps.map((step, index) => (
                  <div key={step} style={{ display: "flex", gap: 14 }}>
                    <div
                      style={{
                        width: 32,
                        height: 32,
                        borderRadius: 999,
                        display: "grid",
                        placeItems: "center",
                        background: "rgba(104, 213, 255, 0.1)",
                        color: "#9bdcff",
                        flexShrink: 0,
                        fontWeight: 700,
                      }}
                    >
                      {index + 1}
                    </div>
                    <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
                      {step}
                    </p>
                  </div>
                ))}
              </div>
            </Card>
            <Card style={{ background: "rgba(6, 16, 30, 0.72)", display: "grid", gap: 14 }}>
              <strong>What the UI needs to feel like</strong>
              <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
                Fast to scan, calm under pressure, and premium without becoming noisy. The dark theme supports focus while keeping the product confident and modern.
              </p>
              <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                <StatusPill label="Focused dark mode" />
                <StatusPill label="Fast to scan" />
                <StatusPill label="Voice-native feel" />
              </div>
            </Card>
          </div>
        </section>

        <section className="page-shell" id="feedback" style={{ display: "grid", gap: 28 }}>
          <SectionTitle
            eyebrow={landingSlides[3].eyebrow}
            title={landingSlides[3].title}
            description={landingSlides[3].description}
          />
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
              gap: 18,
            }}
          >
            <Card style={{ display: "grid", gap: 12 }}>
              <strong>Session timeline</strong>
              <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
                Training sessions keep the call, transcript sync, and feedback generation tied to one record so progress is easier to review over time.
              </p>
            </Card>
            <Card style={{ display: "grid", gap: 12 }}>
              <strong>Transcript review</strong>
              <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
                Reps can look back at specific moments where they lost the thread, missed an objection, or handled a tough moment well.
              </p>
            </Card>
            <Card style={{ display: "grid", gap: 12 }}>
              <strong>Feedback scores</strong>
              <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
                Coaching focuses on objection handling, clarity, confidence, rapport, and closing readiness.
              </p>
            </Card>
          </div>
        </section>

        <section className="page-shell" id="cta" style={{ display: "grid", gap: 28 }}>
          <SectionTitle
            eyebrow={landingSlides[4].eyebrow}
            title={landingSlides[4].title}
            description={landingSlides[4].description}
          />
          <div
            className="panel"
            style={{
              padding: 28,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 20,
              flexWrap: "wrap",
            }}
          >
            <div style={{ display: "grid", gap: 10, maxWidth: 620 }}>
              <strong style={{ fontSize: "1.4rem" }}>Turn more practice into better performance.</strong>
              <p style={{ margin: 0, color: "#9eb0cf", lineHeight: 1.7 }}>
                Give your team a clear place to prepare, practice, and improve before high-stakes customer conversations.
              </p>
            </div>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              <Button to="/workspace">Open workspace</Button>
              <Button variant="secondary" to="/admin">
                Admin login
              </Button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
