import { useEffect, useRef, useState } from "react";

import DailyIframe from "@daily-co/daily-js";

import { Button } from "../../../components/ui/button";
import { Card } from "../../../components/ui/card";
import { EmptyState } from "../../../components/ui/empty-state";
import { Input } from "../../../components/ui/input";
import { NoticeBanner } from "../../../components/ui/notice-banner";

interface DailyCallPanelProps {
  roomUrl: string | null;
  token: string | null;
  sessionReference: string | null;
  onStatusChange?: (message: string) => void;
}

type JoinState = "idle" | "joining" | "joined" | "error";

export function DailyCallPanel({
  roomUrl,
  token,
  sessionReference,
  onStatusChange,
}: DailyCallPanelProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const frameRef = useRef<ReturnType<typeof DailyIframe.createFrame> | null>(null);
  const [joinState, setJoinState] = useState<JoinState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    void teardownFrame();
    setJoinState("idle");
    setErrorMessage(null);
  }, [roomUrl, token]);

  useEffect(() => {
    return () => {
      void teardownFrame();
    };
  }, []);

  async function teardownFrame() {
    if (!frameRef.current) {
      return;
    }

    try {
      await frameRef.current.leave();
    } catch {
      // Ignore leave errors during cleanup so the UI can recover cleanly.
    }

    frameRef.current.destroy();
    frameRef.current = null;
  }

  async function handleJoinCall() {
    if (!roomUrl || !containerRef.current || frameRef.current) {
      return;
    }

    setJoinState("joining");
    setErrorMessage(null);
    onStatusChange?.("Connecting you to the secure practice call...");

    try {
      const frame = DailyIframe.createFrame(containerRef.current, {
        showLeaveButton: true,
        iframeStyle: {
          width: "100%",
          height: "100%",
          border: "0",
          borderRadius: "20px",
          background: "#091321",
        },
      });

      frameRef.current = frame;
      await frame.join(token ? { url: roomUrl, token } : { url: roomUrl });
      setJoinState("joined");
      onStatusChange?.("Your secure practice call is live.");
    } catch (error) {
      await teardownFrame();
      setJoinState("error");
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "We could not join the practice call. Please try again.",
      );
      onStatusChange?.(
        "The secure join could not be completed. Please retry the practice call.",
      );
    }
  }

  async function handleLeaveCall() {
    await teardownFrame();
    setJoinState("idle");
    setErrorMessage(null);
    onStatusChange?.("You left the practice call.");
  }

  return (
    <Card style={{ display: "grid", gap: 18 }}>
      <strong>Join your practice call</strong>
      <Input
        label="Call link"
        value={roomUrl ?? ""}
        readOnly
        hint="This room is joined securely from inside the workspace."
      />
      <Input
        label="Meeting token"
        value={token ?? ""}
        readOnly
        hint="The secure token is applied automatically when you join."
      />
      {sessionReference ? (
        <Input label="Session reference" value={sessionReference} readOnly />
      ) : null}

      {!roomUrl ? (
        <EmptyState
          title="Your call link will appear here"
          description="Start a practice session first, and this card will become your launch point into the live conversation."
        />
      ) : (
        <>
          {joinState === "error" && errorMessage ? (
            <NoticeBanner
              title="Secure join needs another try"
              description={errorMessage}
              tone="warning"
            />
          ) : null}

          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <Button
              type="button"
              onClick={handleJoinCall}
              disabled={joinState === "joining" || joinState === "joined"}
            >
              {joinState === "joining"
                ? "Connecting..."
                : joinState === "joined"
                  ? "Connected"
                  : "Join secure practice call"}
            </Button>
            <Button
              type="button"
              variant="secondary"
              onClick={handleLeaveCall}
              disabled={joinState !== "joined"}
            >
              Leave call
            </Button>
            <Button href={roomUrl} target="_blank" rel="noreferrer" variant="ghost">
              Open room link
            </Button>
          </div>

          <div
            style={{
              minHeight: 520,
              borderRadius: 24,
              border: "1px solid rgba(123, 163, 255, 0.12)",
              background: "rgba(6, 16, 30, 0.72)",
              overflow: "hidden",
            }}
          >
            {joinState === "idle" || joinState === "error" ? (
              <div
                style={{
                  minHeight: 520,
                  display: "grid",
                  placeItems: "center",
                  padding: 24,
                }}
              >
                <EmptyState
                  title="Secure join stays inside this workspace"
                  description="Use the join button above to enter the live practice room with the meeting token already attached."
                />
              </div>
            ) : null}
            <div
              ref={containerRef}
              style={{
                display: joinState === "joined" || joinState === "joining" ? "block" : "none",
                width: "100%",
                height: 520,
              }}
            />
          </div>
        </>
      )}
    </Card>
  );
}
