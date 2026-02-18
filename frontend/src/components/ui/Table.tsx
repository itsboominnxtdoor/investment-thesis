interface TableProps {
  children: React.ReactNode;
  className?: string;
}

export function Table({ children, className = "" }: TableProps) {
  return (
    <div className={`overflow-hidden rounded-lg border border-gray-200 ${className}`}>
      <table className="min-w-full divide-y divide-gray-200">{children}</table>
    </div>
  );
}

interface TableHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export function TableHeader({ children, className = "" }: TableHeaderProps) {
  return (
    <thead className={`bg-gray-50 ${className}`}>
      {children}
    </thead>
  );
}

interface TableRowProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

export function TableRow({ children, className = "", onClick }: TableRowProps) {
  return (
    <tr 
      className={`border-b border-gray-100 last:border-0 ${onClick ? "cursor-pointer hover:bg-gray-50" : ""} ${className}`}
      onClick={onClick}
    >
      {children}
    </tr>
  );
}

interface TableHeadProps {
  children: React.ReactNode;
  className?: string;
}

export function TableHead({ children, className = "" }: TableHeadProps) {
  return (
    <th 
      className={`px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 ${className}`}
    >
      {children}
    </th>
  );
}

interface TableCellProps {
  children: React.ReactNode;
  className?: string;
}

export function TableCell({ children, className = "" }: TableCellProps) {
  return (
    <td className={`px-6 py-4 text-sm text-gray-900 ${className}`}>
      {children}
    </td>
  );
}

interface TableBodyProps {
  children: React.ReactNode;
  className?: string;
}

export function TableBody({ children, className = "" }: TableBodyProps) {
  return (
    <tbody className={`divide-y divide-gray-100 bg-white ${className}`}>
      {children}
    </tbody>
  );
}

interface EmptyStateProps {
  message: string;
  colSpan?: number;
}

export function TableEmpty({ message, colSpan = 1 }: EmptyStateProps) {
  return (
    <TableRow>
      <TableCell className="text-center py-8" >
        <p className="text-gray-500">{message}</p>
      </TableCell>
    </TableRow>
  );
}
