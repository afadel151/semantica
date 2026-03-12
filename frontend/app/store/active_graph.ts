import { defineStore } from "pinia";
interface GraphDetails {
  id: string,
  name: string
}

export const useActiveGraphStore = defineStore('active_graph', {
  state: () => ({
    id: '',
    name: ''
  }),
  getters: {
    getName: (state) => state.name,
    getId: (state) => state.id
  },
  actions: {
    setGraph(graph: GraphDetails) {
      this.$state = graph
    },
    clearGraph() {
      this.$state = { id: '', name: '' }
    }
  },
})