interface CardProps {
  children: React.ReactNode;
  className?: string;
  interactive?: boolean;
  href?: string;
}

export function Card({ children, className = "", interactive = false, href }: CardProps) {
  const baseClasses = `rounded-2xl bg-[var(--color-surface)] border border-[var(--color-border-light)] shadow-sm transition-all duration-300`;
  const interactiveClasses = interactive 
    ? "hover:shadow-md hover:border-[var(--color-border)] hover:-translate-y-0.5 cursor-pointer" 
    : "";
  
  const content = (
    <div className={`${baseClasses} ${interactiveClasses} ${className}`}>
      {children}
    </div>
  );
  
  if (href) {
    return (
      <a href={href} className="block">
        {content}
      </a>
    );
  }
  
  return content;
}
