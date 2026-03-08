export interface GraphsStats {
  total_graphs: number;
  total_triples: number;
  total_subjects: number;
  total_predicates: number;
  total_objects: number;
}
export interface GraphFileStats {
  graph_id: string;
  name: string;
  format: string;
  file_size: number;
  triples_count: number;
  uploaded_at: string;
  subjects_count: number;
  predicates_count: number;
  objects_count: number;
}


export interface Subject {
  id: string;
  graph_id: string;
  prefix_form: string;
  predicate_count: number;
  uri: string;
  rdf_type: string;
}


export interface Predicate {
  uri: string;
  prefix_form: string;
  usage_count: number;
  domain: string | null;
  range: string | null;
  id: string;
  graph_id: string;
}

export interface Object {
  value: string;
  prefix_form: string | null;
  kind: string;
  language: string | null;
  datatype: string | null;
  referenced_by: number;

  id: string;
  graph_id: string;
}

export interface GraphElements {
  subjects: Subject[];
  predicates: Predicate[];
  objects: Object[];
}

/**
 * 
 * "objects": [
    {
      "value": "2014-09-25",
      "prefix_form": null,
      "language": null,
      "kind": "literal",
      "id": "d24bcc9f-3524-47db-9548-a625ee1c97b4",
      "graph_id": "61159550-da23-4911-8e8f-e5e500547b60",
      "datatype": null,
      "referenced_by": 2
    },
 */