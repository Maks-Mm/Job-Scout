export default function EmptyState() {
  return (
    <div className="text-center py-12 bg-gray-50 rounded-lg">
      <p className="text-gray-500">No jobs found matching your criteria</p>
      <p className="text-sm text-gray-400 mt-1">Try adjusting your filters</p>
    </div>
  );
}