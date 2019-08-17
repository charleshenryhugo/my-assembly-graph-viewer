<template>
  <div>
    <v-card
      class="mx-auto"
      color="#F9F9F9"
      max-width="350"
    >

      <v-card-title>
        Current Selection
      </v-card-title>

      <v-card-text>
        <v-treeview
          :items="current_selection.current_contig_or_link_tree"
        >
        </v-treeview>
      </v-card-text>

      <v-divider></v-divider>

    </v-card>

    <v-card
      class="mx-auto"
      max-width="350"
    >
      <v-card-title>
        Graph Info
      </v-card-title>

      <v-card-text>
        <v-treeview
          :items="graph_info.contigs_tree"
        >
        </v-treeview>
        <v-treeview
          :items="graph_info.links_tree"
        >
        </v-treeview>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
// event bus for communication with GraphViewer
import { EventBus } from '../scripts/event-bus.js';

export default {
  name: 'SidePanel',
  components: {
  },
  data() {
    return {
      graph_info_panels: [0, 2],

      current_selection: { 
        current_contig_or_link: 'no selection',
        current_contig_or_link_tree: []
      },

      graph_info: {
        GFA_version: 1.0,
        contigs_tree: [],
        links_tree: []
      }
    }
  },

  created() {
    this.graph_info.contigs_tree = [ {
      id: 'contigs_tree_root',
      name: 'contigs',
      children: []
    } ];

    this.graph_info.links_tree = [ {
      id: 'links_tree_root',
      name: 'links',
      children: []
    } ];
  },

  mounted() {
    var _this = this;

    EventBus.$on( 'currentSelectionUpdated', function(current_selected_object, type) {
      _this.current_selection.current_contig_or_link = current_selected_object;

      if (type === 'contig') {
        _this.current_selection.current_contig_or_link_tree = [ {
          id: 'current_selected_contig',
          name: current_selected_object[0],
          children: [
            { name: `length: ${current_selected_object[2]}` },
            { name: `tag: ${current_selected_object[2]}` },
            {
              name: `sequence`, 
              children: [ { name: current_selected_object[1] } ] 
            }
          ]
        } ];
      } else if (type === 'link') {
        var source = current_selected_object[0], target = current_selected_object[2];
        _this.current_selection.current_contig_or_link_tree = [ {
          id: 'current_selected_link',
          name: `${source}-${target}`,
          children: [
            { name: `cigar: ${current_selected_object[4]}` },
            { name: `tag: ${current_selected_object[5]}` },
            { name: `more options...` }
          ]
        } ];
      }

    });

    EventBus.$on( 'contigsUpdated', function( contigs ) {
      _this.graph_info.contigs_tree[0].children = contigs.map( function(contig) {
        return {
          id: contig[0],
          name: contig[0],
          children: [
            { name: `length: ${contig[2]}` },
            { name: `tag: ${contig[2]}` },
            {
              name: `sequence`, 
              children: [ { name: contig[1] } ] 
            }
          ]
        };
      } );
    });

    EventBus.$on( 'linksUpdated', function( links ) {
      _this.graph_info.links_tree[0].children = links.map( function(link) {
        var source = link[0], target = link[2];
        // TODO remove duplicate links
        // TODO apply id
        return {
          name: `${source}-${target}`,
          children: [
            { name: `cigar: ${link[4]}` },
            { name: `tag: ${link[5]}` },
            { name: `more options...` }
          ]
        };
      } );
    });
  },
}
</script>

<style scoped>
</style>

