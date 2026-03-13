type QueryType = "SELECT" | "CONSTRUCT" | "DESCRIBE" | "ASK" | "INSERT" | "DELETE" | "UPDATE";

type BadgeVariant =
  | "default"
  | "secondary"
  | "destructive"
  | "outline"
  | "rdf"
  | "ontology"
  | "select"
  | "ask"
  | "construct"
  | "describe";

export function mapQueryToVariant(type: QueryType): BadgeVariant {
  switch (type) {
    case "SELECT":
      return "select";
    case "ASK":
      return "ask";
    case "CONSTRUCT":
      return "construct";
    case "DESCRIBE":
      return "describe";
    case "INSERT":
      return "default";
    case "DELETE":
      return "destructive";
    case "UPDATE":
      return "secondary";
    default:
      return "default";
  }
}
