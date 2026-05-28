import ScanScreen from '@/components/ScanScreen';

export default function Palm() {
  return (
    <ScanScreen
      title="Read your palm"
      icon="hand"
      route="palm-scan"
      prompt="Show your dominant palm. Good light, fingers spread."
    />
  );
}
