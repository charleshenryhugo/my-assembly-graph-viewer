<template>
  <div id="CommunitiesViewer"></div>
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
  name: 'CommunitiesViewer',
  components:{
  },

  props: {
    communities: Object // {}
  },

  data() {
    return {
    }
  },

  watch: {
    communities() {
      this.renderCommunities();
    },
  },

  mounted(){
    this.renderCommunities();
  },

  methods: {
    renderCommunities(){
      var _this = this;

      var community_centers = []
      Object.keys( _this.communities ).forEach( function(id) {
        community_centers.push( {
          data: { 
            id: id, // _this.communities[id].community_id === id
            size: 10 * Math.log2(_this.communities[id].size),
            description: `community_${id}, size=${_this.communities[id].size}`
          }
        } )
      } );

      cy = this.$cytoscape( {
        container: document.querySelector('#CommunitiesViewer'),

        elements: {
            nodes: community_centers,
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
        var selected_community_id = evt.target.id();
        EventBus.$emit( 'communitySelectionUpdated', _this.communities[selected_community_id] );
      } );
    }
  }
}
</script>

<style scoped>
  #CommunitiesViewer {
    height: 100%;
    width: 100%;
    position: absolute;
    left: 0;
    top: 0;
  }
</style>