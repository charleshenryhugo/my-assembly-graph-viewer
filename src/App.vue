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
        <span class="hidden-sm-and-down">highly interactive assembly graph viewer</span>
      </v-toolbar-title>
      <v-text-field
        flat
        solo-inverted
        hide-details
        prepend-inner-icon=""
        label="Search"
        class="hidden-sm-and-down"
      ></v-text-field>
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
          <GraphViewer/>
        </v-layout>
      </v-container>
    </v-content>

    <v-bottom-navigation app>
    </v-bottom-navigation>
  </v-app>
</template>

<script>
import GraphViewer from './components/GraphViewer';
import SidePanel from './components/SidePanel';

export default {
  name: 'App',
  components: {
    GraphViewer,
    SidePanel
  },

  props: {
    source: String,
  },

  data: () => ({
    drawer: null,
    items: [
    ]
  }),
}
</script>
