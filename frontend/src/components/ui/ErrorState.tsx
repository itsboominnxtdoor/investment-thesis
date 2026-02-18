"use client";

import { Card } from "./Card";

interface Props {
  title?: string;
  message: string;
  variant?: "error" | "empty";
  onRetry?: () => void;
}

export function ErrorState({
  title,
  message,
  variant = "error",
  onRetry,
}: Props) {
  const isError = variant === "error";

  return (
    <Card>
      <div className="py-6 text-center">
        <div
          className={`mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full ${
            isError ? "bg-red-100" : "bg-gray-100"
          }`}
        >
          {isError ? (
            <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          ) : (
            <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-2.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
            </svg>
          )}
        </div>
        {title && (
          <h3 className={`mb-1 font-semibold ${isError ? "text-red-800" : "text-gray-700"}`}>
            {title}
          </h3>
        )}
        <p className={`text-sm ${isError ? "text-red-600" : "text-gray-500"}`}>{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Retry
          </button>
        )}
      </div>
    </Card>
  );
}
