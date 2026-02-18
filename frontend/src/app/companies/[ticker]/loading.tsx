export default function CompanyDetailLoading() {
  return (
    <div className="space-y-6">
      {/* Header skeleton */}
      <div className="mb-6">
        <div className="flex items-center gap-3">
          <div className="animate-pulse h-12 w-12 rounded-xl bg-gray-200"></div>
          <div className="space-y-2">
            <div className="animate-pulse h-8 w-64 rounded-lg bg-gray-200"></div>
            <div className="animate-pulse h-4 w-48 rounded-lg bg-gray-100"></div>
          </div>
        </div>
      </div>

      {/* Tabs skeleton */}
      <div className="relative overflow-x-auto">
        <div className="flex gap-1 rounded-xl bg-gray-200 p-1">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="animate-pulse h-10 w-28 rounded-lg bg-white"></div>
          ))}
        </div>
      </div>

      {/* Content skeleton */}
      <div className="space-y-6">
        {/* Business Profile / Thesis skeleton */}
        <div className="rounded-2xl border border-gray-200 bg-white p-6">
          <div className="animate-pulse mb-6 flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gray-200"></div>
            <div className="space-y-2">
              <div className="h-5 w-40 rounded bg-gray-200"></div>
              <div className="h-3 w-24 rounded bg-gray-100"></div>
            </div>
          </div>
          <div className="space-y-3">
            <div className="h-4 w-full rounded bg-gray-100"></div>
            <div className="h-4 w-5/6 rounded bg-gray-100"></div>
            <div className="h-4 w-4/6 rounded bg-gray-100"></div>
          </div>
        </div>

        {/* Three case cards skeleton */}
        <div className="grid gap-4 md:grid-cols-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="rounded-2xl border border-gray-200 bg-white p-5">
              <div className="animate-pulse mb-3 flex items-center justify-between">
                <div className="h-5 w-20 rounded bg-gray-200"></div>
                <div className="h-6 w-16 rounded-full bg-gray-300"></div>
              </div>
              <div className="space-y-2">
                <div className="h-3 w-full rounded bg-gray-100"></div>
                <div className="h-3 w-5/6 rounded bg-gray-100"></div>
              </div>
            </div>
          ))}
        </div>

        {/* Metrics skeleton */}
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="rounded-xl bg-gray-50 p-4">
              <div className="animate-pulse space-y-2">
                <div className="h-3 w-20 rounded bg-gray-200"></div>
                <div className="h-6 w-24 rounded bg-gray-300"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
