import { Redirect } from 'expo-router';

// First run lands on onboarding. In the real app this gate would check
// whether the user has completed setup and send returning users to /today.
export default function Index() {
  return <Redirect href="/onboarding/welcome" />;
}
