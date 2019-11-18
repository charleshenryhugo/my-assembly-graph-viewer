<template>
  <div 
    id="PathsGraphViewer"
  >
  </div>
</template>

<script>
// event bus for communication with SidePanel
import { EventBus } from '../scripts/event-bus.js';

// d3-format
let d3 = Object.assign( {}, require('d3-format') );

/**
 * cytoscape instance
 * browser crash while stored in vue data
 */
let cy = null;

export default {
  name: 'PathsGraphViewer',
  components: {
  },

  props: {
    graph_dir: String,
  },

  data() {
    return {
      current_selection: {
        current_contig: null,
        current_link: null
      },

      cy_opts: {
        style: null,
        layout_options: null
      },

      contigs: null,
      links: null,

      contig_lens: null,
      MAX_CONTIG_LEN: 0.0,
      MIN_CONTIG_LEN: 0.0,
      MAX_CONTIG_DISPLAY_LEN: 25.0,
      MIN_CONTIG_DISPLAY_LEN: 3.0,

      path_line_spacing: 15.0,

    }
  },

  created() {
    // load cytoscape css style
    this.cy_opts.style = require('../scripts/paths-viewer-style.js');
  },

  mounted() {
    var _this = this;

    var rel_graph_dir = this.graph_dir.match(/(data\/.*cluster_.*\d|data\/isolated_contigs_cluster)$/)[0]
    console.log('PathsGraphViewer starts loading graph: ' + rel_graph_dir)

    var contigs_file = `${rel_graph_dir}/contigs.json`;
    var links_file = `${rel_graph_dir}/links.json`;

    this.$axios.get( contigs_file ).then( function(contigs_response) {

      _this.$axios.get( links_file ).then( function(links_response) {
        _this.contigs = contigs_response.data;
        _this.links = links_response.data;
        _this.renderCy();
        _this.cyAdjust();
      } );

    } );

  },

  methods: {

    /**
     * load and render cytoscape graph using this.contigs and this.links. 
     * execute while init and update
     */
    renderCy() {
      var _this = this;

      // contig actual lengths
      this.contig_lens = this.contigs.map( c => Number(c[2].slice(5)) );
      this.MIN_CONTIG_LEN = Math.min(...this.contig_lens);
      this.MAX_CONTIG_LEN = Math.max(...this.contig_lens);

      cy = this.$cytoscape({
        container: document.querySelector('#PathsGraphViewer'),
        elements: {
          nodes: this.contigs.map( c => (
            { data: { id: c[0], length: Number(c[2].slice(5)) } } 
          ) ),
        },
        style: this.cy_opts.style
      });

      this.links.forEach( l => {
        if ( !cy.$(`#${l[0]}${l[2]}`).length && !cy.$(`#${l[2]}${l[0]}`).length ) {
          cy.add({
            data: {
              id: `${l[0]}${l[2]}`,
              source: l[0],
              target: l[2],
              link: l,
            }
          });
        }
      });

      // render all paths
      this.renderPaths();
      // this.renderLinks();

      // let cy resize with #PathsGraphViewer
      this.makeCyResizable();

    }, // end of renderCy()

    /**
     * render all paths
     */
    renderPaths() {
      var _this = this;

      let all_paths = cy.elements().cytoscapeAllPaths();
      cy.nodes().remove();
      // console.log(all_paths);

      all_paths.forEach( (path, path_id) => {
        var x = 0;
        // add contigs
        path.forEach( ele => {
          if ( ele.isEdge() ) { return; }

          var contig = {
            id: `path-${path_id}-${ele.data().id}`,
            actual_id: ele.data().id,
            length: ele.data().length,
          }

          if ( cy.$(`#${contig.id}-5-3`).length ) { return; }

          var x_step = _this.displayLength( contig.length );
          x += x_step;
          _this.addContig(
            contig,
            { x: x, y: _this.path_line_spacing * path_id },
          );
          x += x_step + 2;

        });
        // add links
        path.forEach( ele => {
          if ( !ele.isEdge() ) { return; }
          _this.addLink( ele.data().link, path_id);
        });
      });
    },

    /**
     * add a link to cy
     * @param {Object} link ['contig1_id', '+' ,'contig2_id', '-', ...]
     * @param {Number} path_id i
     */
    addLink(link, path_id) {
      var source = `path-${path_id}-${link[0]}`;
      var target = `path-${path_id}-${link[2]}`;

      var control_point_param = 0.1;
      var control_point_weights = [0, 0];
      
      if (link[1] === '+') {
        source = `${source}-3`;
        control_point_weights[0] = control_point_param;
      } else if (link[1] === '-') {
        source = `${source}-5`;
        control_point_weights[0] = -control_point_param;
      }
      if (link[3] === '+') {
        target = `${target}-5`;
        control_point_weights[1] = -control_point_param + 1;
      } else if (link[3] === '-') {
        target = `${target}-3`;
        control_point_weights[1] = control_point_param + 1;
      }

      var delta_x = cy.$(`#${target}`).position().x - cy.$(`#${source}`).position().x;
      var control_point_distances = [ Math.abs(delta_x), Math.abs(delta_x) ].map( n => 0.4 * n );

      if (link[0] === link[2]) { // self loop
        control_point_weights = [-0.2, 1.2];
        control_point_distances = [ Math.abs(delta_x), Math.abs(delta_x) ].map( n => 0.2 * n );
      }
      cy.add({
        data: {
          id: `${source}-${target}`,
          source: source,
          target: target,
          line_color: '#006666',
          control_point_distances: control_point_distances,
          control_point_weights: control_point_weights,
        },
        classes: 'contig-link-edge',
      });
    },

    /**
     * fit range from=>[lower, upper] to=>[lower, upper]
     * @param {Number} num 
     * @param {Array} from [0:lower, 1:upper]
     * @param {Array} to [0:lower, 1:upper]
     */
    fitRange(num, from, to) {
      var fit_rate = ( to[1] - to[0] ) / ( from[1] - from[0] );
      return ( fit_rate * ( num - from[0] ) + to[0] );
    },

    /**
     * how long to display the contig.
     * ( namely, display_length or logic_length ).
     * fit the length into [ MIN_CONTIG_DISPLAY_LEN, MAX_CONTIG_DISPLAY_LEN ]
     * @param {Number} contig_actual_length
     * @return {Number} contig_display_length ( or contig_logic_length )
     */
    displayLength(contig_actual_length) {
      if ( this.MAX_CONTIG_LEN - this.MIN_CONTIG_LEN === 0 ) {
        return this.MAX_CONTIG_DISPLAY_LEN;
      }
      return this.fitRange(
        contig_actual_length,
        [this.MIN_CONTIG_LEN, this.MAX_CONTIG_LEN],
        [this.MIN_CONTIG_DISPLAY_LEN, this.MAX_CONTIG_DISPLAY_LEN]
      );
    },

    /**
     * add a contig to cy
     * @param {Object} contig { id, length(actual_length) }
     * @param {Object} pos { x, y }
     */
    addContig(contig, pos) {
      var _this = this;

      cy.add( _this.makeContig(contig, pos) );

      cy.automove({
        nodesMatching: cy.$(`#${contig.id}-3, #${contig.id}-5`),
        reposition: 'drag',
        dragWith: cy.$(`#${contig.id}-3, #${contig.id}-5`),
      });

    },

    /**
     * make a contig Object for Cytoscape to render
     * @param {Object} contig { id, actual_id, length(actual_length) }
     * @param {Object} pos { x, y }
     * @return {Array} [ contig-end-node-box, 5-end, 3-end, contig_inner_edge ]
     */
    makeContig(contig, pos) {
      return [
        {
          data: { id: `${contig.id}-5`, name: '', },
          position: { x: pos.x - this.displayLength(contig.length), y: pos.y },
          classes: 'contig-end-node'
        },
        {
          data: { id: `${contig.id}-3`, name: '', },
          position: { x: pos.x + this.displayLength(contig.length), y: pos.y },
          classes: 'contig-end-node'
        },
        {
          data: { 
            id: `${contig.id}-5-3`,
            name: `${contig.actual_id}`,
            source: `${contig.id}-5`,
            target: `${contig.id}-3`,
            length: contig.length
          },
          classes: 'contig-inner-edge',
        }
      ];
    },

    /**
     * adjust cytoscape viewport, pan, etc.
     */
    cyAdjust() {
      cy.viewport({
        zoom: 5,
        pan: { x: 50, y: 50 }
      });
      cy.minZoom(1);
      cy.maxZoom(10);
    },

    /**
     * make cy resize with #PathsGraphViewer
     * this may not work for some browsers
     */
    makeCyResizable() {
      // listen to #PathsGraphViewer resize event
      new ResizeObserver( entries => {
        cy.resize();
      }).observe(
        document.querySelector('#PathsGraphViewer')
      );
    },

  }
}
</script>

<style>
  #PathsGraphViewer {
    height: 100%;
    width: 100%;
    position: relative;
    left: 0;
    top: 0;
  }
</style>