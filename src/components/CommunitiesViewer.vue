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
    renderCommunities() {
      var _this = this;

      var community_centers = [];
      Object.keys( _this.communities ).forEach( function(id) {
        community_centers.push( {
          data: { 
            id: id, // _this.communities[id].community_id === id
            size: 10 * Math.log2(_this.communities[id].size),
            description: `#${id}, size ${_this.communities[id].size}`
          }
        } );
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
          {
            selector: '.hightlight-node',
            style: {
              'border-color': '#ffb266',
            }
          },
          {
            selector: 'edge',
            style: {
              'width': 1,
              'line-color': '#ffb266',
            }
          }
        ],

        layout: {
          name: 'grid',
        },

      } );

      // user taps on a node
      cy.nodes().on('tap', function(evt) {
        var selected_community_id = evt.target.id();
        EventBus.$emit( 'communitySelectionUpdated', _this.communities[selected_community_id] );
        
        // load edges connected to this community ball
        _this.renderExpansionEdges(selected_community_id)
      } );
    },

    /**
     * load expansion edges when user taps a community node
     */
    renderExpansionEdges(selected_community_id) {
      var _this = this;
      cy.edges().remove();
      cy.nodes().removeClass('hightlight-node');
      cy.$(`#${selected_community_id}`).addClass('hightlight-node');

      Object.keys( _this.communities[selected_community_id].expansion_edges ).forEach( function(target_community_id) {
        cy.add({
          data: {
            id: `${selected_community_id}-${target_community_id}`,
            source: selected_community_id,
            target: target_community_id,
          }
        });

        // user taps on community link
        cy.$(`#${selected_community_id}-${target_community_id}`).on('tap', function(evt) {
          EventBus.$emit( 'currentSelectionUpdated',
                          _this.communities[selected_community_id].expansion_edges[target_community_id],
                          'community_link');
        });

        // highlight the connected nodes
        cy.$(`#${target_community_id}`).addClass('hightlight-node');
      } );
    },

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