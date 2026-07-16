// Onboarding.tsx — the container state machine that drives the 7-screen first-run flow and,
// on completion, builds the real birth Profile from everything captured and hands it up
// (onComplete) so the app can setProfile() + run real math. Ported from the prototype's
// `Onboarding` container (window.OBScreens graph).
//
//   welcome → name → place → time → reveal → signup ─┬→ otp → email → done → (Enter) → app
//                                                    └→ done  (Google / email — already have it)
//                                                 └ (from Welcome) login → done → app
//
// The phone path is India's ONE door, so it is the only branch that then needs `email` (the
// number got them in; the email is the way back in if they lose the phone). Google/email
// signups skip that screen because those keys already carry an address.
//
// `otp` only appears on the phone path, and Truecaller users (dev build) skip it entirely —
// one tap and they are through. That is why SignUp decides and this file just routes: the
// container never needs to know which key was used.
import React, { useState } from "react";
import { View } from "react-native";
import { Profile } from "../api/config";
import { P } from "./kit";
import { OnbData, emptyData, buildProfileFromData } from "./data";
import { Welcome } from "./Welcome";
import { NameGender, BirthPlace, BirthTime } from "./steps";
import { Reveal } from "./Reveal";
import { SignUp, OtpStep, AddEmail, Login, Done } from "./Auth";

export function Onboarding({ onComplete }: { onComplete: (profile: Profile | null) => void }) {
  const [step, setStep] = useState("welcome");
  const [data, setData] = useState<OnbData>(emptyData);
  const [phone, setPhone] = useState("");   // E.164, captured by SignUp's phone path
  const patch = (p: Partial<OnbData>) => setData((d) => ({ ...d, ...p }));
  const go = (to: string) => setStep(to);

  const enter = () => onComplete(buildProfileFromData(data));
  const common = { data, patch };

  let body: React.ReactNode;
  if (step === "welcome") body = <Welcome onBegin={() => go("name")} onLogin={() => go("login")} />;
  else if (step === "name") body = <NameGender {...common} step={1} onBack={() => go("welcome")} onNext={() => go("place")} />;
  else if (step === "place") body = <BirthPlace {...common} step={2} onBack={() => go("name")} onNext={() => go("time")} />;
  else if (step === "time") body = <BirthTime {...common} step={3} onBack={() => go("place")} onNext={() => go("reveal")} />;
  else if (step === "reveal") body = <Reveal {...common} step={4} onBack={() => go("time")} onNext={() => go("signup")} />;
  else if (step === "signup") body = (
    <SignUp {...common} step={5} onBack={() => go("reveal")} onDone={() => go("done")}
      onPhone={(e164: string) => { setPhone(e164); go("otp"); }} />
  );
  else if (step === "otp") body = <OtpStep phone={phone} step={5} onBack={() => go("signup")} onDone={() => go("email")} />;
  else if (step === "email") body = (
    <AddEmail {...common} step={5} onBack={() => go("otp")} onDone={() => go("done")} onSkip={() => go("done")} />
  );
  else if (step === "login") body = <Login onBack={() => go("welcome")} onFresh={() => go("welcome")} onDone={() => go("done")} />;
  else if (step === "done") body = <Done data={data} onEnter={enter} onReplay={() => { setData(emptyData); go("welcome"); }} />;
  else body = <Welcome onBegin={() => go("name")} onLogin={() => go("login")} />;

  return <View style={{ flex: 1, backgroundColor: P.paper }}>{body}</View>;
}
// OnbData / emptyData / buildProfileFromData live in ./data (shared, cycle-free).
