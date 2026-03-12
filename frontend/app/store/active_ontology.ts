import { defineStore } from "pinia";

interface OntologyDetails {
  id: string;
  name: string;
  format: string;
}

export const useActiveOntologiesStore = defineStore("active_ontologies", {
  state: () => ({
    ontologies: [] as OntologyDetails[],
  }),

  getters: {
    getOntologies: (state) => state.ontologies,
    getOntologiesIds: (state) => state.ontologies.map((o) => o.id),
  },

  actions: {
    addOntology(detail: OntologyDetails) {
      this.ontologies.push(detail);
    },
    removeOntology(id: string | string[] | undefined) {
      this.ontologies = this.ontologies.filter((o) => o.id !== id);
    },
    isActive(id: string | string[] | undefined) {
        let exists = this.ontologies.filter((o) => o.id == id)
        if (exists.length == 0) {
            return false
        }
        return true
    },
  },
});
