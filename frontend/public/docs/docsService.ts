export interface Chapter {
  id: number;
  title: string;
  text: string;
  images: string[];
}

export async function fetchTOC(): Promise<Chapter[]> {
  const res = await fetch("/docs/data.json");
  if (!res.ok) throw new Error("Couldn’t load docs.json");
  return res.json();
}
