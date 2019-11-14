<template>
  <v-app id="vuetify-app">

    <v-navigation-drawer
      v-model="drawer"
      :clipped="$vuetify.breakpoint.lgAndUp"
      :width="350"
      app
    >
      <sidePanel/>
    </v-navigation-drawer>

    <v-app-bar
      :clipped-left="$vuetify.breakpoint.lgAndUp"
      color="blue darken-3"
      dark
      app
    >
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title
        style="width: 30%"
        class="ml-0 pl-4"
      >
        <span class="hidden-sm-and-down">VILAG</span>
      </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>

    <v-content>
      <v-container
        fluid
        fill-height
      >
        <v-layout
          align-center
          justify-center
        >
          <ClustersViewer
            v-if="viewer_type==='clusters'"
          />

          <Split
            :gutterSize="5"
            :direction="'vertical'"
            v-if="viewer_type==='graph'"
          >
            <SplitArea
              :size="50"
              :minSize="10"
            >
              <GraphViewer
                :graph_dir="graph_dir"
              />
            </SplitArea>
            <SplitArea
              :size="50"
              :minSize="10"
            >
              <PathsGraphViewer
                :graph_dir="graph_dir"
              />
            </SplitArea>
          </Split>

          <CommunitiesViewer
            v-if="viewer_type==='communities'"
            :communities="communities"
          />
        </v-layout>
      </v-container>
    </v-content>

    <v-bottom-navigation app>
    </v-bottom-navigation>
  </v-app>
</template>

<script>
import ClustersViewer from './components/ClustersViewer';
import CommunitiesViewer from './components/CommunitiesViewer';
import GraphViewer from './components/GraphViewer';
import PathsGraphViewer from './components/PathsGraphViewer';
import SidePanel from './components/SidePanel';

// event bus for communication with SidePanel
import { EventBus } from './scripts/event-bus.js';

export default {
  name: 'App',
  components: {
    ClustersViewer,
    CommunitiesViewer,
    GraphViewer,
    PathsGraphViewer,
    SidePanel,
  },

  data() {
    return {
      // left side panel
      drawer: null,

      /**
       * viewer_type: which component v-content renders
       * 'clusters', 'communities', 'graph'
       * initialized by 'clusters'
       */
      viewer_type: null,

      // last rendered graph dir
      graph_dir: null,

      // last rendered community
      communities: null,
    };
  },

  created() {
    this.viewer_type = 'clusters'
  },

  mounted() {
    var _this = this;

    EventBus.$on( 'viewer_type_graph', function(graph_dir) {
      _this.viewer_type = 'graph';
      _this.graph_dir = graph_dir;
    } );

    EventBus.$on( 'viewer_type_communities', function(communities) {
      _this.viewer_type = 'communities';
      _this.communities = communities;
    } );

    EventBus.$on( 'viewer_type_clusters', function() {
      _this.viewer_type = 'clusters';
    } )
  },

  methods: {
  },

}
</script>
