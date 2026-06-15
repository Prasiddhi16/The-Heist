import { useState } from "react";
import { LoginScreen } from "./pages/LoginScreen";
import { CasesScreen } from "./pages/CaseScreen";
import { InvestigateScreen } from "./pages/InvestigationScreen";
import { AccuseScreen } from "./pages/AccuseScreen";
import { ResultScreen } from "./pages/Results";
import { LeaderboardScreen } from "./pages/Leaderboard";
import { CASES, SUSPECTS, Case, Suspect } from "./data/gameData";



type Screen = "login" | "cases" | "investigate" | "accuse" | "result" | "leaderboard";

export default function App() {
  const [screen, setScreen] = useState<Screen>("login");
  const [username, setUsername] = useState("");
  const [totalPoints, setTotalPoints] = useState(0);
  const [selectedCase, setSelectedCase] = useState<Case | null>(null);
  const [accusedSuspect, setAccusedSuspect] = useState<Suspect | null>(null);
  const [lastResult, setLastResult] = useState<{ correct: boolean; points: number } | null>(null);
  const [prevScreen, setPrevScreen] = useState<Screen>("cases");

  function handleLogin(name: string) {
    setUsername(name);
    setScreen("cases");
  }

  function handleSelectCase(caseId: string) {
    const c = CASES.find(x => x.id === caseId) || null;
    setSelectedCase(c);
    setAccusedSuspect(null);
    setScreen("investigate");
  }

  function handleAccuse(suspect: Suspect) {
    setAccusedSuspect(suspect);
    setScreen("accuse");
  }

  function handleConfirmAccuse(suspect: Suspect) {
    if (!selectedCase) return;
    const culprit = SUSPECTS[selectedCase.id]?.find(s => s.isCulprit);
    const correct = culprit?.id === suspect.id;
    const earned = correct ? selectedCase.points : 0;
    setTotalPoints(p => p + earned);
    setLastResult({ correct, points: earned });
    setAccusedSuspect(suspect);
    setScreen("result");
  }

  function handleChangeSuspect(suspect: Suspect) {
    setAccusedSuspect(suspect);
  }

  function handleLeaderboard() {
    setPrevScreen(screen);
    setScreen("leaderboard");
  }

  function handleBackFromLeaderboard() {
    setScreen(prevScreen);
  }

  const suspects = selectedCase ? (SUSPECTS[selectedCase.id] || []) : [];
  const culprit = selectedCase ? suspects.find(s => s.isCulprit) : undefined;

  return (
    <div className="min-h-screen" style={{ background: "var(--background)" }}>
      {screen === "login" && (
        <LoginScreen onLogin={handleLogin} />
      )}

      {screen === "cases" && (
        <CasesScreen
          cases={CASES}
          username={username}
          onSelectCase={handleSelectCase}
          onLeaderboard={handleLeaderboard}
          onLogout={() => setScreen("login")}
        />
      )}

      {screen === "investigate" && selectedCase && (
        <InvestigateScreen
          caseData={selectedCase}
          suspects={suspects}
          onAccuse={handleAccuse}
          onBack={() => setScreen("cases")}
        />
      )}

      {screen === "accuse" && selectedCase && accusedSuspect && (
        <AccuseScreen
          caseData={selectedCase}
          suspect={accusedSuspect}
          allSuspects={suspects}
          onConfirm={handleConfirmAccuse}
          onChangeSuspect={handleChangeSuspect}
          onBack={() => setScreen("investigate")}
        />
      )}

      {screen === "result" && selectedCase && accusedSuspect && lastResult && culprit && (
        <ResultScreen
          caseData={selectedCase}
          accusedSuspect={accusedSuspect}
          isCorrect={lastResult.correct}
          culprit={culprit}
          points={lastResult.points}
          onPlayAgain={() => setScreen("cases")}
          onHome={() => setScreen("cases")}
          onLeaderboard={handleLeaderboard}
        />
      )}

      {screen === "leaderboard" && (
        <LeaderboardScreen
          username={username}
          userPoints={totalPoints}
          onBack={handleBackFromLeaderboard}
        />
      )}
    </div>
  );
}
