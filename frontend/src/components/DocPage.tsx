// src/components/DocPage.tsx
interface DocPageProps {
  text: string;
  images: string[];
}

export function DocPage({ text, images }: DocPageProps) {
  return (
    <article className="prose prose-lg max-w-none mx-auto">
      {text ? <div dangerouslySetInnerHTML={{ __html: text }} /> : <p>No content.</p>}
      {images.length > 0 && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-4">
          {images.map((src, i) => (
            <img key={i} src={src} alt={`Fig ${i + 1}`} className="rounded shadow" />
          ))}
        </div>
      )}
    </article>
  );
}




