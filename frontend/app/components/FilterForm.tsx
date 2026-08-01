//frontend/app/components/FilterForm.tsx

"use client";

import { useState, type FormEvent } from "react";

interface Filter {
    country: string;
    city: string;
    language: string;
    keywords: string;
    jobCategory: string;
    employmentType: string;
    source?: string;
    minSalary: number;
    maxSalary: number;
}

interface FilterFormProps {
    onSave: (filter: Filter) => void;
    initialFilters: Filter;
}

// Top cities by country
const CITIES_BY_COUNTRY: Record<string, Array<{ value: string; label: string }>> = {
    Germany: [
        // Major economic hubs (Top Tier)
        { value: "Berlin", label: "Berlin 🏛️" },
        { value: "Munich", label: "Munich 💰" },
        { value: "Hamburg", label: "Hamburg ⚓" },
        { value: "Frankfurt", label: "Frankfurt 💹" },
        { value: "Cologne", label: "Cologne 🏗️" },
        { value: "Düsseldorf", label: "Düsseldorf 👔" },
        { value: "Stuttgart", label: "Stuttgart 🚗" },
        { value: "Nuremberg", label: "Nuremberg 🏭" },
        // Strong economic centers (Second Tier)
        { value: "Essen", label: "Essen 🏢" },
        { value: "Dortmund", label: "Dortmund 📊" },
        { value: "Bremen", label: "Bremen 🚢" },
        { value: "Dresden", label: "Dresden 🖥️" },
        { value: "Leipzig", label: "Leipzig 📈" },
        { value: "Hanover", label: "Hanover 📋" },
        { value: "Mannheim", label: "Mannheim 🏗️" },
        // Regional economic centers (Third Tier)
        { value: "Augsburg", label: "Augsburg 🔧" },
        { value: "Bonn", label: "Bonn 🏛️" },
        { value: "Münster", label: "Münster 📚" },
        { value: "Karlsruhe", label: "Karlsruhe 🔬" },
        { value: "Freiburg", label: "Freiburg 🌿" },
        { value: "Wiesbaden", label: "Wiesbaden 🏢" },
        { value: "Kiel", label: "Kiel ⚓" },
        { value: "Magdeburg", label: "Magdeburg 🏗️" },
    ],
    Austria: [
        { value: "Vienna", label: "Wien 🏛️" },
        { value: "Graz", label: "Graz 🏗️" },
        { value: "Linz", label: "Linz 🏭" },
        { value: "Salzburg", label: "Salzburg 🎵" },
        { value: "Innsbruck", label: "Innsbruck ⛰️" },
        { value: "Klagenfurt", label: "Klagenfurt 🌊" },
        { value: "Villach", label: "Villach 🏗️" },
        { value: "Wels", label: "Wels 📊" },
        { value: "St. Pölten", label: "Sankt Pölten 🏢" },
        { value: "Dornbirn", label: "Dornbirn 🏭" },
        { value: "Steyr", label: "Steyr 🏗️" },
        { value: "Bregenz", label: "Bregenz 🌊" },
    ],
    Switzerland: [
        { value: "Zurich", label: "Zürich 💰" },
        { value: "Geneva", label: "Genève 🏛️" },
        { value: "Bern", label: "Bern 🏢" },
        { value: "Basel", label: "Basel 🧪" },
        { value: "Lausanne", label: "Lausanne 🏗️" },
        { value: "Lucerne", label: "Luzern ⛰️" },
        { value: "St. Gallen", label: "St. Gallen 📚" },
        { value: "Winterthur", label: "Winterthur 🏭" },
        { value: "Biel", label: "Biel ⏰" },
        { value: "Lugano", label: "Lugano ☀️" },
        { value: "Thun", label: "Thun 🏗️" },
        { value: "Köniz", label: "Köniz 🏢" },
    ],
    Liechtenstein: [
        { value: "Vaduz", label: "Vaduz 🏛️" },
        { value: "Schaan", label: "Schaan 🏗️" },
        { value: "Triesen", label: "Triesen 🏭" },
    ],
    Luxembourg: [
        { value: "Luxembourg City", label: "Luxembourg 🏛️" },
        { value: "Esch-sur-Alzette", label: "Esch-sur-Alzette 🏗️" },
        { value: "Differdange", label: "Differdange 🏭" },
    ],
};

// Job categories covering the majority of Teilzeit / Minijob postings
const JOB_CATEGORIES = [
    { value: "all", label: "Alle Kategorien" },
    { value: "buero", label: "🏢 Büro & Verwaltung" },
    { value: "verkauf", label: "🛒 Verkauf & Einzelhandel" },
    { value: "gastronomie", label: "🍽 Gastronomie & Tourismus" },
    { value: "logistik", label: "🚚 Transport, Logistik & Lager" },
    { value: "bau", label: "🏗 Bau, Handwerk & Produktion" },
    { value: "kundenservice", label: "📞 Kundenservice & Call Center" },
    { value: "pflege", label: "❤️ Soziales & Pflege" },
    { value: "it", label: "💻 IT & Technik" },
    { value: "ausbildung", label: "🎓 Ausbildung" },
    { value: "praktikum", label: "📚 Praktika" },
    { value: "mini", label: "💼 Mini- & Nebenjobs" },
    { value: "weitere", label: "📦 Sonstige Jobs" },
];

export default function FilterForm({ onSave, initialFilters }: FilterFormProps) {
    const [country, setCountry] = useState(initialFilters.country ?? "Germany");
    const [city, setCity] = useState(initialFilters.city ?? "");
    const [language, setLanguage] = useState(initialFilters.language ?? "de");
    const [minSalary, setMinSalary] = useState<number | "">(initialFilters.minSalary ?? "");
    const [maxSalary, setMaxSalary] = useState<number | "">(initialFilters.maxSalary ?? "");
    const [keywords, setKeywords] = useState(initialFilters.keywords ?? "");
    const [jobCategory, setJobCategory] = useState(initialFilters.jobCategory ?? "all");
    const [employmentType, setEmploymentType] = useState(initialFilters.employmentType ?? "all");

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        onSave({
            country,
            city,
            language,
            keywords,
            jobCategory,
            employmentType,
            minSalary: minSalary === "" ? 0 : Number(minSalary),
            maxSalary: maxSalary === "" ? 0 : Number(maxSalary),
        });
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Country
                    </label>
                    <select
                        value={country}
                        onChange={(e) => {
                            setCountry(e.target.value);
                            setCity(""); // Reset city when country changes to avoid invalid state
                        }}
                        className="w-full border rounded-lg p-2"
                    >
                        <option value="Germany">Germany</option>
                        <option value="Austria">Austria</option>
                        <option value="Switzerland">Switzerland</option>
                        <option value="Liechtenstein">Liechtenstein</option>
                        <option value="Luxembourg">Luxembourg</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Language
                    </label>
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="w-full border rounded-lg p-2"
                    >
                        <option value="de">German</option>
                        <option value="en">English</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        City / Region
                    </label>
                    <select
                        value={city}
                        onChange={(e) => setCity(e.target.value)}
                        className="w-full border rounded-lg p-2"
                    >
                        <option value="">🌍 Alle Städte</option>
                        {CITIES_BY_COUNTRY[country as keyof typeof CITIES_BY_COUNTRY]?.map((c) => (
                            <option key={c.value} value={c.value}>
                                {c.label}
                            </option>
                        ))}
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
                        className="w-full border rounded-lg p-2"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Job Category
                    </label>
                    <select
                        value={jobCategory}
                        onChange={(e) => setJobCategory(e.target.value)}
                        className="w-full border rounded-lg p-2"
                    >
                        {JOB_CATEGORIES.map((category) => (
                            <option key={category.value} value={category.value}>
                                {category.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Employment Type
                    </label>
                    <select
                        value={employmentType}
                        onChange={(e) => setEmploymentType(e.target.value)}
                        className="w-full border rounded-lg p-2"
                    >
                        <option value="all">Alle</option>
                        <option value="fulltime">Vollzeit</option>
                        <option value="parttime">Teilzeit</option>
                        <option value="mini">Minijob</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Min Salary (€)
                    </label>
                    <input
                        type="number"
                        value={minSalary}
                        onChange={(e) => setMinSalary(e.target.value === "" ? "" : Number(e.target.value))}
                        className="w-full border rounded-lg p-2"
                        placeholder="e.g., 150"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Max Salary (€)
                    </label>
                    <input
                        type="number"
                        value={maxSalary}
                        onChange={(e) => setMaxSalary(e.target.value === "" ? "" : Number(e.target.value))}
                        className="w-full border rounded-lg p-2"
                        placeholder="e.g., 550"
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