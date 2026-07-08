// frontend/app/components/JobCard.tsx
interface Job {
  id: number | string;  // Changed from number to number | string
  title: string;
  company: string;
  city: string;
  salary: string;
  date?: string;
  url: string;
  source: string;
}

export default function JobCard({ job }: { job: Job }) {
  return (
    <div className="bg-white border rounded-lg p-4 mb-3 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">
            {job.title}
          </h3>
          <p className="text-gray-600 mt-1">{job.company}</p>
          <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-500">
            <span>📍 {job.city}</span>
            <span>💰 {job.salary}</span>
            {job.date && <span>🕒 {job.date}</span>}
            <span>🔗 {job.source}</span>
          </div>
        </div>
        <a
          href={job.url}
          target="_blank"
          rel="noopener noreferrer"
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-blue-700"
        >
          Apply
        </a>
      </div>
    </div>
  );
}