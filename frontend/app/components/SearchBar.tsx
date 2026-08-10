//frontend/app/components/SearchBar.tsx

"use client";

import { useState, type ChangeEvent, type KeyboardEvent } from "react";

export default function SearchBar({ onSearch }: { onSearch: (term: string) => void }) {
  const [term, setTerm] = useState("");

  const handleSearch = () => {
    onSearch(term);
  };

  return (
    <div className="flex gap-2">
      <input
        type="text"
        placeholder="Search jobs by title or company..."
        value={term}
        onChange={(e: ChangeEvent<HTMLInputElement>) => setTerm(e.target.value)}
        onKeyPress={(e: KeyboardEvent<HTMLInputElement>) => e.key === "Enter" && handleSearch()}
        className="flex-1 border rounded-lg p-2"
      />
      <button
        onClick={handleSearch}
        className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700"
      >
        Search
      </button>
    </div>
  );
}