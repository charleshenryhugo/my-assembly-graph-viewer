import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify';
import VueSplit from 'vue-split-panel'; 

// http://js.cytoscape.org/
import cytoscape from 'cytoscape'
import klay from 'cytoscape-klay';
import automove from 'cytoscape-automove';
import cytoscapeAllPaths from 'cytoscape-all-paths';

// https://medium.com/@negarjf/how-to-access-a-static-json-file-in-vue-cli-3-8943dc343f95
import axios from 'axios';

cytoscape.use( klay );
cytoscape.use( automove );
cytoscape.use( cytoscapeAllPaths );

Vue.use(VueSplit);

Vue.prototype.$cytoscape = cytoscape;
Vue.prototype.$axios = axios;

Vue.config.productionTip = false

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app')
