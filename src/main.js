import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify';

// http://js.cytoscape.org/
import cytoscape from 'cytoscape'
import klay from 'cytoscape-klay';
import dagre from 'cytoscape-dagre';

cytoscape.use( dagre );

// https://medium.com/@negarjf/how-to-access-a-static-json-file-in-vue-cli-3-8943dc343f95
import axios from 'axios';

cytoscape.use( klay );
Vue.prototype.$cytoscape = cytoscape;
Vue.prototype.$axios = axios;

Vue.config.productionTip = false

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app')
