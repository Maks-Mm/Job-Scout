"use client";

import { useState } from "react";

interface Filter {
    city: string;
    minSalary: number;
    maxSalary: number;
    keywords: string;
}

interface FilterFormProps {
    onSave: (filter: Filter) => void;
    initialFilters: Filter;
}

export default function FilterForm({ onSave, initialFilters }: FilterFormProps) {
    const [city, setCity] = useState(initialFilters.city);
    const [minSalary, setMinSalary] = useState(initialFilters.minSalary);
    const [maxSalary, setMaxSalary] = useState(initialFilters.maxSalary);
    const [keywords, setKeywords] = useState(initialFilters.keywords);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave({
            city,
            minSalary,
            maxSalary,
            keywords,
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        City
                    </label>
                    <select
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="w-full border rounded-lg p-2"
                    >
                        <option value="Munich">Munich</option>
                        <option value="Augsburg">Augsburg</option>
                        <option value="Both">Both</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Keywords (optional)
                    </label>
                    <input
                        type="text"
                        placeholder="e.g., Frontend, Admin, Sales"
                        value={keywords}
                        onChange={(e) => setKeywords(e.target.value)}
                        className="input-default" // <-- Clean and consistent
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Min Salary (€)
                    </label>
                    <input
                        type="number"
                        value={minSalary}
                        onChange={(e) => setMinSalary(Number(e.target.value))}
                        className="w-full border rounded-lg p-2"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Max Salary (€)
                    </label>
                    <input
                        type="number"
                        value={maxSalary}
                        onChange={(e) => setMaxSalary(Number(e.target.value))}
                        className="w-full border rounded-lg p-2"
                    />
                </div>
            </div>

            <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700"
            >
                Search Jobs
            </button>
        </form>
    );
}