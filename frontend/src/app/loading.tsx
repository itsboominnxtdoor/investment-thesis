export default function DashboardLoading() {
  return (
    <div className="space-y-8">
      {/* Hero skeleton */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700 px-8 py-12 sm:px-12">
        <div className="animate-pulse">
          <div className="h-8 w-64 rounded-lg bg-white/20"></div>
          <div className="mt-4 h-4 w-96 rounded-lg bg-white/10"></div>
          <div className="mt-8 flex gap-8">
            <div className="h-12 w-20 rounded-lg bg-white/10"></div>
            <div className="h-12 w-20 rounded-lg bg-white/10"></div>
            <div className="h-12 w-20 rounded-lg bg-white/10"></div>
          </div>
        </div>
      </div>

      {/* Stats skeleton */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="rounded-2xl bg-white p-6 shadow-sm">
            <div className="animate-pulse">
              <div className="h-4 w-24 rounded bg-gray-200"></div>
              <div className="mt-3 h-8 w-16 rounded bg-gray-300"></div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters skeleton */}
      <div className="flex flex-wrap gap-3">
        <div className="animate-pulse h-10 w-64 rounded-full bg-gray-200"></div>
        <div className="animate-pulse h-10 w-40 rounded-full bg-gray-200"></div>
        <div className="animate-pulse h-10 w-40 rounded-full bg-gray-200"></div>
      </div>

      {/* Company cards skeleton */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="rounded-2xl border border-gray-200 bg-white p-5">
            <div className="animate-pulse flex items-start gap-4">
              <div className="h-12 w-12 rounded-xl bg-gray-200"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 w-20 rounded bg-gray-200"></div>
                <div className="h-3 w-32 rounded bg-gray-100"></div>
                <div className="flex gap-2">
                  <div className="h-5 w-16 rounded-full bg-gray-100"></div>
                  <div className="h-5 w-12 rounded-full bg-gray-100"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
