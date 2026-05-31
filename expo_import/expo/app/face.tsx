import ScanScreen from '@/components/ScanScreen';

export default function Face() {
  return (
    <ScanScreen
      title="Read your face"
      icon="eye"
      route="face-read"
      prompt="Look straight ahead. Soft, even light. No glasses if possible."
    />
  );
}
