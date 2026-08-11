// frontend/app/components/FilterForm.tsx

"use client";

import { useState, type FormEvent, type ChangeEvent, type ReactElement } from "react";

// ===== INTERFACES =====
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

// ===== DATA =====
const CITIES_BY_COUNTRY: Record<string, Array<{ value: string; label: string }>> = {
    Germany: [
        { value: "Berlin", label: "Berlin 🏛️" },
        { value: "Munich", label: "Munich 💰" },
        { value: "Hamburg", label: "Hamburg ⚓" },
        { value: "Frankfurt", label: "Frankfurt 💹" },
        { value: "Cologne", label: "Cologne 🏗️" },
        { value: "Düsseldorf", label: "Düsseldorf 👔" },
        { value: "Stuttgart", label: "Stuttgart 🚗" },
        { value: "Nuremberg", label: "Nuremberg 🏭" },
        { value: "Essen", label: "Essen 🏢" },
        { value: "Dortmund", label: "Dortmund 📊" },
        { value: "Bremen", label: "Bremen 🚢" },
        { value: "Dresden", label: "Dresden 🖥️" },
        { value: "Leipzig", label: "Leipzig 📈" },
        { value: "Hanover", label: "Hanover 📋" },
        { value: "Mannheim", label: "Mannheim 🏗️" },
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
    Belgien: [
        { value: "Brussels", label: "Brüssel 🏛️" },
        { value: "Schaerbeek", label: "Schaerbeek 🏢" },
        { value: "Anderlecht", label: "Anderlecht ⚽" },
        { value: "Ixelles", label: "Ixelles/Elsene 🎓" },
        { value: "Antwerp", label: "Antwerpen 🚢" },
        { value: "Ghent", label: "Gent 🏗️" },
        { value: "Bruges", label: "Brügge 🌊" },
        { value: "Leuven", label: "Leuven 📚" },
        { value: "Mechelen", label: "Mechelen 🏭" },
        { value: "Aalst", label: "Aalst 📊" },
        { value: "Hasselt", label: "Hasselt 🏢" },
        { value: "Sint-Niklaas", label: "Sint-Niklaas 🏗️" },
        { value: "Oostende", label: "Oostende ⚓" },
        { value: "Genk", label: "Genk 🏭" },
        { value: "Roeselare", label: "Roeselare 🏢" },
        { value: "Liège", label: "Lüttich 🏗️" },
        { value: "Charleroi", label: "Charleroi 🏭" },
        { value: "Namur", label: "Namur 🏛️" },
        { value: "Mons", label: "Mons 🏢" },
        { value: "Tournai", label: "Tournai 🏗️" },
        { value: "Verviers", label: "Verviers 🏭" },
        { value: "La Louvière", label: "La Louvière 🏢" },
        { value: "Arlon", label: "Arlon 🏛️" },
        { value: "Bastogne", label: "Bastogne 🎖️" },
        { value: "Marche-en-Famenne", label: "Marche-en-Famenne 🏞️" },
        { value: "Eupen", label: "Eupen 🏛️" },
        { value: "Sankt Vith", label: "Sankt Vith 🏞️" },
    ],
};

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

const COUNTRIES_WITH_FLAGS = [
    { value: "Germany", label: "🇩🇪 Germany" },
    { value: "Austria", label: "🇦🇹 Austria" },
    { value: "Switzerland", label: "🇨🇭 Switzerland" },
    { value: "Liechtenstein", label: "🇱🇮 Liechtenstein" },
    { value: "Luxembourg", label: "🇱🇺 Luxembourg" },
    { value: "Belgien", label: "🇧🇪 Belgien" },
];

// ===== COMPONENT =====
export default function FilterForm({ onSave, initialFilters }: FilterFormProps) {
    const [country, setCountry] = useState<string>(initialFilters.country ?? "");
    const [city, setCity] = useState<string>(initialFilters.city ?? "");
    const [language, setLanguage] = useState<string>(initialFilters.language ?? "de");
    const [minSalary, setMinSalary] = useState<number | "">(initialFilters.minSalary ?? "");
    const [maxSalary, setMaxSalary] = useState<number | "">(initialFilters.maxSalary ?? "");
    const [keywords, setKeywords] = useState<string>(initialFilters.keywords ?? "");
    const [jobCategory, setJobCategory] = useState<string>(initialFilters.jobCategory ?? "all");
    const [employmentType, setEmploymentType] = useState<string>(initialFilters.employmentType ?? "all");
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = (e: FormEvent<HTMLFormElement>): void => {
        e.preventDefault();
        if (!country) {
            setError("Bitte wähle zuerst ein Land aus.");
            return;
        }

        setError(null);
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

    const getLanguageOptions = (): ReactElement => {
        if (country === "Belgien") {
            return (
                <>
                    <option value="de">🇩🇪 Deutsch</option>
                    <option value="nl">🇳🇱 Nederlands</option>
                    <option value="fr">🇫🇷 Français</option>
                    <option value="en">🇬🇧 English</option>
                </>
            );
        }
        if (country === "Switzerland") {
            return (
                <>
                    <option value="de">🇩🇪 Deutsch</option>
                    <option value="fr">🇫🇷 Français</option>
                    <option value="it">🇮🇹 Italiano</option>
                    <option value="en">🇬🇧 English</option>
                </>
            );
        }
        if (country === "Luxembourg") {
            return (
                <>
                    <option value="de">🇩🇪 Deutsch</option>
                    <option value="fr">🇫🇷 Français</option>
                    <option value="en">🇬🇧 English</option>
                    <option value="lb">🇱🇺 Lëtzebuergesch</option>
                </>
            );
        }
        return (
            <>
                <option value="de">🇩🇪 German</option>
                <option value="en">🇬🇧 English</option>
            </>
        );
    };

    const handleCountryChange = (e: ChangeEvent<HTMLSelectElement>): void => {
        const newCountry = e.target.value;
        setCountry(newCountry);
        setCity("");
        setError(null);

        // Auto-set language based on country
        if (newCountry === "Belgien" || newCountry === "Switzerland" || newCountry === "Luxembourg") {
            setLanguage("de");
        } else {
            setLanguage("de");
        }
    };

    const handleCityChange = (e: ChangeEvent<HTMLSelectElement>): void => {
        setCity(e.target.value);
    };

    const handleLanguageChange = (e: ChangeEvent<HTMLSelectElement>): void => {
        setLanguage(e.target.value);
    };

    const handleKeywordsChange = (e: ChangeEvent<HTMLInputElement>): void => {
        setKeywords(e.target.value);
    };

    const handleJobCategoryChange = (e: ChangeEvent<HTMLSelectElement>): void => {
        setJobCategory(e.target.value);
    };

    const handleEmploymentTypeChange = (e: ChangeEvent<HTMLSelectElement>): void => {
        setEmploymentType(e.target.value);
    };

    const handleMinSalaryChange = (e: ChangeEvent<HTMLInputElement>): void => {
        const value = e.target.value;
        setMinSalary(value === "" ? "" : Number(value));
    };

    const handleMaxSalaryChange = (e: ChangeEvent<HTMLInputElement>): void => {
        const value = e.target.value;
        setMaxSalary(value === "" ? "" : Number(value));
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
                        onChange={handleCountryChange}
                        className="w-full border rounded-lg p-2"
                    >
                        <option value="" disabled>
                            🌍 Land wählen
                        </option>
                        {COUNTRIES_WITH_FLAGS.map((c) => (
                            <option key={c.value} value={c.value}>
                                {c.label}
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Language
                    </label>
                    <select
                        value={language}
                        onChange={handleLanguageChange}
                        className="w-full border rounded-lg p-2"
                    >
                        {getLanguageOptions()}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        City / Region
                    </label>
                    <select
                        value={city}
                        onChange={handleCityChange}
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
                        onChange={handleKeywordsChange}
                        className="w-full border rounded-lg p-2"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Job Category
                    </label>
                    <select
                        value={jobCategory}
                        onChange={handleJobCategoryChange}
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
                        onChange={handleEmploymentTypeChange}
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
                        onChange={handleMinSalaryChange}
                        className="w-full border rounded-lg p-2"
                        placeholder="e.g., 150"
                        min="0"
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Max Salary (€)
                    </label>
                    <input
                        type="number"
                        value={maxSalary}
                        onChange={handleMaxSalaryChange}
                        className="w-full border rounded-lg p-2"
                        placeholder="e.g., 550"
                        min="0"
                    />
                </div>
            </div>

            {error && (
                <p className="text-sm text-red-600 -mt-2">
                    {error}
                </p>
            )}

            <button
                type="submit"
                className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
                🔍 Search Jobs
            </button>
        </form>
    );
}