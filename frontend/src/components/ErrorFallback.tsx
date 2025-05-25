export function ErrorFallback({ message }: { message: string }) {
  return <div className="p-4 text-red-600">Error: {message}</div>;
}