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

// Top economically developed cities in Germany with job market data
const GERMAN_CITIES = [
    // Major economic hubs (Top Tier)
    { value: "Berlin", label: "Berlin 🏛️", region: "East" },
    { value: "Munich", label: "Munich 💰", region: "South" },
    { value: "Hamburg", label: "Hamburg ⚓", region: "North" },
    { value: "Frankfurt", label: "Frankfurt 💹", region: "West" },
    { value: "Cologne", label: "Cologne 🏗️", region: "West" },
    { value: "Düsseldorf", label: "Düsseldorf 👔", region: "West" },
    { value: "Stuttgart", label: "Stuttgart 🚗", region: "South" },
    { value: "Nuremberg", label: "Nuremberg 🏭", region: "South" },
    
    // Strong economic centers (Second Tier)
    { value: "Essen", label: "Essen 🏢", region: "West" },
    { value: "Dortmund", label: "Dortmund 📊", region: "West" },
    { value: "Bremen", label: "Bremen 🚢", region: "North" },
    { value: "Dresden", label: "Dresden 🖥️", region: "East" },
    { value: "Leipzig", label: "Leipzig 📈", region: "East" },
    { value: "Hanover", label: "Hanover 📋", region: "North" },
    { value: "Mannheim", label: "Mannheim 🏗️", region: "West" },
    
    // Regional economic centers (Third Tier)
    { value: "Augsburg", label: "Augsburg 🔧", region: "South" },
    { value: "Bonn", label: "Bonn 🏛️", region: "West" },
    { value: "Münster", label: "Münster 📚", region: "West" },
    { value: "Karlsruhe", label: "Karlsruhe 🔬", region: "South" },
    { value: "Freiburg", label: "Freiburg 🌿", region: "South" },
    { value: "Wiesbaden", label: "Wiesbaden 🏢", region: "West" },
    { value: "Kiel", label: "Kiel ⚓", region: "North" },
    { value: "Magdeburg", label: "Magdeburg 🏗️", region: "East" },
];

// Group cities by region for better organization
const CITIES_BY_REGION = GERMAN_CITIES.reduce((acc, city) => {
    if (!acc[city.region]) {
        acc[city.region] = [];
    }
    acc[city.region].push(city);
    return acc;
}, {} as Record<string, typeof GERMAN_CITIES>);

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
                        City / Region
                    </label>
                    <select
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="w-full border rounded-lg p-2"
                    >
                        <optgroup label="🏛️ Top Economic Hubs">
                            {GERMAN_CITIES.slice(0, 8).map((c) => (
                                <option key={c.value} value={c.value}>
                                    {c.label}
                                </option>
                            ))}
                        </optgroup>
                        <optgroup label="📊 Strong Economic Centers">
                            {GERMAN_CITIES.slice(8, 15).map((c) => (
                                <option key={c.value} value={c.value}>
                                    {c.label}
                                </option>
                            ))}
                        </optgroup>
                        <optgroup label="🏗️ Regional Centers">
                            {GERMAN_CITIES.slice(15).map((c) => (
                                <option key={c.value} value={c.value}>
                                    {c.label}
                                </option>
                            ))}
                        </optgroup>
                        <option value="Both">🌍 All Cities</option>
                    </select>
                    <p className="text-xs text-gray-500 mt-1">
                        {GERMAN_CITIES.find(c => c.value === city)?.label || "Select a city"}
                    </p>
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
                        className="w-full border rounded-lg p-2"
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
                        placeholder="e.g., 40000"
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
                        placeholder="e.g., 80000"
                    />
                </div>
            </div>

            <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
                🔍 Search Jobs
            </button>
        </form>
    );
}