interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "green" | "amber" | "red" | "gray" | "blue" | "yellow" | "purple";
  className?: string;
  size?: "sm" | "md";
}

const variantClasses: Record<string, string> = {
  default: "bg-blue-500/10 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400",
  green: "bg-green-500/10 text-green-600 dark:bg-green-500/20 dark:text-green-400",
  amber: "bg-amber-500/10 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400",
  red: "bg-red-500/10 text-red-600 dark:bg-red-500/20 dark:text-red-400",
  gray: "bg-gray-500/10 text-gray-600 dark:bg-gray-500/20 dark:text-gray-400",
  blue: "bg-blue-500/10 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400",
  yellow: "bg-yellow-500/10 text-yellow-600 dark:bg-yellow-500/20 dark:text-yellow-400",
  purple: "bg-purple-500/10 text-purple-600 dark:bg-purple-500/20 dark:text-purple-400",
};

const sizeClasses: Record<string, string> = {
  sm: "px-2 py-0.5 text-xs",
  md: "px-2.5 py-1 text-xs",
};

export function Badge({ children, variant = "default", className = "", size = "md" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full font-medium ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
    >
      {children}
    </span>
  );
}
