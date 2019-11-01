<template>
  <div id="ClustersViewer"></div>
</template>

<script>
// event bus for communication with SidePanel
import { EventBus } from '../scripts/event-bus.js';

/**
 * cytoscape instance
 * browser crash while stored in vue data
 */
let cy = null;

export default {
  name: 'ClustersViewer',
  components:{
  },

  data() {
    return {
      clusters_overview: null
    }
  },

  created() {
  },

  mounted() {
    var _this = this;
    var clusters_overview_file = 'data/overview.json';
    this.$axios.get( clusters_overview_file ).then( function(response) {
      _this.clusters_overview = response.data;
      _this.renderClusters();
      _this.cyAdjust();
    } );

  },

  methods: {
    renderClusters() {
      var _this = this;

      let cluster_centers = this.clusters_overview.map( function(cluster) {
        return {
          data: { 
            id: cluster.cluster_id,
            size: 10 * Math.log2(cluster.size),
            description: `#${cluster.cluster_id}, size ${cluster.size}`
          }
        }
      } );

      cy = this.$cytoscape( {
        container: document.querySelector('#ClustersViewer'),

        elements: {
            nodes: cluster_centers,
        },

        style: [
          {
            selector: 'node',
            style: {
              'shape': 'ellipse',
              'border-width': 2,
              'border-color': '#00cc88',
              'background-color': '#fffff0',
              'content': 'data(description)',
              'font-size': 10,
              'color': '#808080',
              'text-valign': 'bottom',
              'text-halign': 'center',
              'width': 'data(size)',
              'height': 'data(size)'
            }
          },
        ],

        layout: {
          name: 'grid',
        },

      } );

      cy.nodes().on('tap', function(evt) {
        var selected_cluster_id = evt.target.id();
        EventBus.$emit( 'clusterSelectionUpdated', _this.clusters_overview[selected_cluster_id] );
      } );

    },

    /**
     * adjust cytoscape viewport, pan, etc.
     */
    cyAdjust() {
      cy.minZoom(1);
      cy.maxZoom(5);
    },

  }
}
</script>

<style scoped>
  #ClustersViewer {
    height: 100%;
    width: 100%;
    position: absolute;
    left: 0;
    top: 0;
  }
</style>