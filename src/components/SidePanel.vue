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

        <v-breadcrumbs
          class="pa-2"
          :items="current_selection.community_layers"
          divider="/"
          v-if="current_selection.community_layers.length"
        ></v-breadcrumbs>

        <v-btn
          class="pa-2"
          text
          color="primary"
          @click.stop="clusterClicked"
          v-if="current_selection.current_cluster_description"
        >
          <h5>{{ current_selection.current_cluster_description }}</h5>
        </v-btn>

        <v-btn
          class="pa-2"
          text
          color="primary"
          @click.stop="communityClicked"
          v-if="current_selection.current_community_description"
        >
          <h5>{{ current_selection.current_community_description }}</h5>
        </v-btn>


        <v-treeview
          open-on-click
          activatable
          hoverable
          dense
          :items="current_selection.current_contig_or_link_tree"
          v-if="current_selection.current_contig_or_link_tree.length"
        >
          <template v-slot:label="{ item, open, selected }">
            <TreeviewItemTemplate :item="item"/>
          </template>
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
        <v-btn
          text
          color="primary"
          @click.stop="loadWholeGraph"
        >
          <h5>reload whole graph</h5>
        </v-btn>
      </v-card-title>

      <v-text-field
        class="pa-2"
        v-model="search_box_input"
        outlined
        clearable
        clear-icon="mdi-close-circle-outline"
        append-icon="mdi-magnify"
        @click:append="search_contig_by_id"
        label="Search contig by id"
      >
      </v-text-field>

      <v-card-text>
        <v-treeview
          open-on-click
          activatable
          hoverable
          dense
          :items="graph_info.contigs_tree"
          v-if="graph_info.contigs_tree.length"
        >
          <template v-slot:label="{ item, open, selected }">
            <TreeviewItemTemplate :item="item"/>
          </template>
        </v-treeview>

        <v-treeview
          open-on-click
          activatable
          hoverable
          dense
          :items="graph_info.links_tree"
          v-if="graph_info.links_tree.length"
        >
          <template v-slot:label="{ item, open, selected }">
            <TreeviewItemTemplate :item="item"/>
          </template>
        </v-treeview>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
// event bus for communication with GraphViewer
import { EventBus } from '../scripts/event-bus.js';
import TreeviewItemTemplate from './TreeviewItemTemplate.vue';

export default {
  name: 'SidePanel',
  components: {
    TreeviewItemTemplate,
  },
  data() {
    return {
      search_box_input: null,

      current_selection: {
        community_layers: [],

        current_cluster: null,
        current_cluster_description: null,

        current_community: null,
        current_community_description: null,

        current_contig_or_link: null,
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
    this.current_selection.community_layers = [];
    this.current_selection.current_contig_or_link_tree = [];

    this.graph_info.contigs_tree = [];

    this.graph_info.links_tree = [];
  },

  mounted() {
    var _this = this;

    // user's tap on a cluster ball
    // load tapped cluster's description
    EventBus.$on( 'clusterSelectionUpdated',
                  (current_selected_object) => _this.clusterSelectionUpdated(current_selected_object));

    // user's tap on a community ball
    // load tapped community's description
    EventBus.$on( 'communitySelectionUpdated',
                  (current_selected_object) => _this.communitySelectionUpdated(current_selected_object) );

    EventBus.$on( 'currentSelectionUpdated',
                  (current_selected_object, type) => _this.currentSelectionUpdated(current_selected_object, type) );

    EventBus.$on( 'contigsUpdated', (contigs) => _this.contigsUpdated(contigs) );

    EventBus.$on( 'linksUpdated', (links) => _this.linksUpdated(links) );
  },

  methods: {
    // callbacks for EventBus event

    /**
     * clusterSelectionUpdated
     */
    clusterSelectionUpdated(current_selected_object) {
      var _this = this;
      _this.current_selection.current_cluster = current_selected_object;
      _this.current_selection.current_cluster_description = '' +
            `cluster#${current_selected_object.cluster_id}, ` +
            `${current_selected_object.size} contigs, ` +
            `${Object.keys(current_selected_object.communities).length} communities`;
    },

    /**
     * communitySelectionUpdated
     */
    communitySelectionUpdated(current_selected_object) {
      var _this = this;
      _this.current_selection.current_community = current_selected_object;
      _this.current_selection.current_community_description = '' +
            `community_${current_selected_object.community_id}, ` +
            `${current_selected_object.size} contigs, ` +
            `${Object.keys(current_selected_object.communities).length} communities`;
    },

    /**
     * currentSelectionUpdated
     * @param type: 'contig', 'link', 'current_selected_link'
     */
    currentSelectionUpdated(current_selected_object, type) {
      var _this = this;
      _this.current_selection.current_contig_or_link = current_selected_object;

      if (type === 'contig') {
        var contig = current_selected_object;
        _this.current_selection.current_contig_or_link_tree = [ {
          id: 'current_selected_contig', name: contig[0],
          children: [
            { id: `${contig[0]}-${contig[2]}`, name: contig[2] },
            { name: `${contig[1].slice(0,600)} ...` }
          ]
        } ];
      } else if (type === 'link') {
        var l = current_selected_object;
        _this.current_selection.current_contig_or_link_tree = [{
          id: 'current_selected_link',
          name: `${l[0]}-${l[2]}`,
          children: [
            { id: l.join(''), name: l.join(' ') },
          ]
        }];
      } else if (type === 'community_link') {
        _this.current_selection.current_contig_or_link_tree = [{
          id: 'current_selected_community_link', name: 'links between the 2 communities',
          children: current_selected_object.map( function(l) {
            return {
              id: l.join(''), name: l.join(' '),
            }
          })
        }];
      }

    },

    /**
     * contigsUpdated: graph changed => contigs changed
     */
    contigsUpdated( contigs ) {
      var _this = this;
      _this.graph_info.contigs_tree = [ {
        id: 'contigs_tree_root', name: 'contigs',
        children: contigs.map( function(contig) {
          return {
            id: contig[0],
            name: contig[0],
            children: [
              { id: `${contig[0]}-${contig[2]}`, name: contig[2] },
              { name: `${contig[1].slice(0,600)} ...` }
            ]
          };
        } )
      } ];
    },

    /**
     * linksUpdated: graph changed => links changed
     */
    linksUpdated( links ) {
      var _this = this;
      _this.graph_info.links_tree = [ {
        id: 'links_tree_root', name: 'links',
        children: links.map( function(l) {
          return {
            id: l.join(''),
            name: l.join(' ')
          };
        } )
      } ];
    },
    // end callbacks for EventBus event

    /**
     * current cluster description's button clicked
     */
    clusterClicked() {
      var _this = this;
      if ( Object.keys(_this.current_selection.current_cluster.communities).length === 0 ){
        // send data to App.vue, render graph
        EventBus.$emit( 'viewer_type_graph', _this.current_selection.current_cluster.cluster_dir );
      } else {
        EventBus.$emit( 'viewer_type_communities', _this.current_selection.current_cluster.communities );
        // send data to App.vue, render communities
      }

      // update breadbrumbs
      _this.current_selection.community_layers = [
        { text: `cluster ${_this.current_selection.current_cluster.cluster_id}` }
      ];
    },

    /**
     * current community description's button clicked
     */
    communityClicked() {
      var _this = this;
      if ( Object.keys(_this.current_selection.current_community.communities).length === 0 ){
        // send data to App.vue, render graph
        EventBus.$emit( 'viewer_type_graph', _this.current_selection.current_community.community_dir );
      } else {
        EventBus.$emit( 'viewer_type_communities', _this.current_selection.current_community.communities );
        // send data to App.vue, render communities
      }
      // update breadcrumbs
      var community_layers = _this.current_selection.current_community.community_dir
          .match(/(data\/.*cluster_.*\d|data\/isolated_contigs_cluster)$/)[0].split('/').slice(2);

      _this.current_selection.community_layers = [{
        text: `cluster ${_this.current_selection.current_cluster.cluster_id}`
      }]
      community_layers.forEach( c => {
        _this.current_selection.community_layers.push({ text: `Community${c}` });
      });
    },

    /**
     * whole graph button clicked
     */
    loadWholeGraph() {
      this.current_selection.current_cluster_description = null;
      this.current_selection.current_community_description = null;
      this.current_selection.community_layers = [];
      this.current_selection.current_contig_or_link_tree = [];
      this.graph_info.contigs_tree = [];
      this.graph_info.links_tree = [];
      EventBus.$emit( 'viewer_type_clusters' );
    },

    /**
     * search contig by id
     * from current GraphViewer
     */
    search_contig_by_id() {
      EventBus.$emit('search_contig_by_id', this.search_box_input);
    }
  }
}
</script>

<style scoped>
</style>

