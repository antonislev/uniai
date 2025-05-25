// src/components/DocNav.tsx
import { Chapter } from "../services/docsService";

interface DocNavProps {
  toc: Chapter[];
  onSelect: (id: number) => void;
}

export function DocNav({ toc, onSelect }: DocNavProps) {
  return (
    <ul className="space-y-1">
      {toc.map((c) => (
        <li key={c.id}>
          <button
            className="w-full text-left px-4 py-2 rounded hover:bg-gray-200 transition"
            onClick={() => onSelect(c.id)}
          >
            {c.title}
          </button>
        </li>
      ))}
    </ul>
  );
}


