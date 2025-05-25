export function Loader({ message }: { message?: string }) {
  return <div className="flex items-center justify-center h-screen">{message || 'Loading…'}</div>;
}