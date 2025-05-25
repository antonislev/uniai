export interface Chapter {
  id: number;
  title: string;
  text: string;
  images: string[];
}

export async function fetchToc(): Promise<Chapter[]> {
  const res = await fetch("/toc");
  if (!res.ok) throw new Error("Failed to fetch TOC");
  return res.json();
}

