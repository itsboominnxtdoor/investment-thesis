import { Badge } from "./ui/Badge";

interface Props {
  score: number | null;
}

export function ThesisIntegrityBadge({ score }: Props) {
  if (score === null || score === undefined) {
    return <Badge variant="gray">No Score</Badge>;
  }

  let variant: "green" | "amber" | "red";
  if (score >= 8) {
    variant = "green";
  } else if (score >= 5) {
    variant = "amber";
  } else {
    variant = "red";
  }

  return <Badge variant={variant}>Integrity: {score.toFixed(1)}</Badge>;
}
