interface NodeElement {
    id : string
    label: string
    type : string
}
interface EdgeElement {
    id: string
    label: string
    source: string
    target: string
}

export interface Element {
   data : NodeElement | EdgeElement
}

export interface GraphMeta {
    node_count : number
    edge_count : number
    graph_id : string
    name : string
    truncated : boolean
} 

export interface VisualisationData {
    meta: GraphMeta
    elements : Element[]
}