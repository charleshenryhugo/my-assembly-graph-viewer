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
      MAX_CONTIG_DISPLAY_LEN: 50.0,
      MIN_CONTIG_DISPLAY_LEN: 6.0,

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
            data: { id: `${l[0]}${l[2]}`, source: l[0], target: l[2] }
          });
        }
      });

      // render all paths
      this.renderPaths();

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

      var line = 0;
      all_paths.forEach( path => {
        var x = 0;
        path.forEach( ele => {
          var ele_id = ele.data().id;
          if ( ele.isEdge() ) { return; }

          if ( cy.$(`#${ele_id}-5-3`).length ) { return; }

          var x_step = _this.displayLength( ele.data().length );
          x += x_step;
          _this.addContig(
            ele.data(), { x: x, y: 10 * line } 
          );
          x += x_step + 1;

        });
        line += 1;
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
     * @param {Object} c { id, length(actual_length) }
     */
    addContig(c, pos) {
      var _this = this;
      cy.add( _this.makeContig(c, pos) );
      cy.automove({
        nodesMatching: cy.$(`#${c.id}-3, #${c.id}-5`),
        reposition: 'drag',
        dragWith: cy.$(`#${c.id}-3, #${c.id}-5`),
      });

    },

    /**
     * make a contig Object for Cytoscape to render
     * @param {Object} contig { id, length(actual_length) }
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
            name: `${contig.id}`,
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