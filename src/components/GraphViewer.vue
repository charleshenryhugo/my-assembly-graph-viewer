<template>
  <div id="cy"></div>
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
  name: 'GraphViewer',
  components: {
  },

  data() {
    return {
      current_selection: {
        current_cluster: 0,
        current_community: 0,
        current_contig: null,
        current_link: null
      },

      cy_opts: {
        style: null,
        layout_options: null
      },

      assembler: null,
      contigs: null,
      links: null,

      contig_ids: null,
      contig_lens: null,
      MAX_CONTIG_LEN: 0.0,
      MIN_CONTIG_LEN: 0.0,
      MAX_CONTIG_DISPLAY_LEN: 25.0,
      MIN_CONTIG_DISPLAY_LEN: 3.0,

      ruler_render_start_pos: {
        x: 0, y: 50
      }
    }
  },

  created() {
    // load cytoscape css style and layout options
    this.cy_opts.style = require('../scripts/style.js');
    this.cy_opts.layout_options = require('../scripts/layout.js');
  },

  mounted() {

    // dynamically read json data ( /data/xxx.json in public folder )
    // this.current_selection.current_cluster = 15;
    // this.current_selection.current_community = -1;
    var init_load = {
      contigs_file: 'data/miniasm_contigs_cluster_15.json',
      links_file: 'data/miniasm_links_cluster_15.json'
    }
    var _this = this;
    this.$axios.get( init_load.contigs_file ).then( function(contigs_response) {

      _this.$axios.get( init_load.links_file ).then( function(links_response) {
        // console.log( contigs_response.data )
        // console.log( links_response.data )
        _this.contigs = contigs_response.data;
        _this.links = links_response.data;
        _this.renderCy();
        _this.renderRuler();
        _this.cyAdjust();

        // send contigs and links data to SidePanel
        EventBus.$emit( 'contigsUpdated', _this.contigs );
        EventBus.$emit( 'linksUpdated', _this.links );
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
      
      this.contig_ids = this.contigs.map( c => c[0] );
      // contigs centers position
      let contig_centers = this.contigs.map(function(c) {
        return {
          data: { id: c[0] }
        };
      });
      // links among contigs
      let contig_centers_links = this.links.map(function(l) {
        if ( _this.contig_ids.includes( (l[0], l[2]) ) ) {
          return {
            data: {
              id: `${l[0]}${l[2]}`, source: l[0], target: l[2]
            }
          };
        }
      })

      cy = this.$cytoscape({
        container: document.querySelector('#cy'),

        elements: {
            nodes: contig_centers,
            edges: contig_centers_links
        },

        // https://github.com/cytoscape/cytoscape.js-klay
        layout: this.cy_opts.layout_options,

        style: this.cy_opts.style
      });

      // render contigs according to this.contigs
      this.renderContigs();

      // render contig-link-edge among contigs
      this.renderLinks();

    }, // end of renderCy()

    /**
     * render contigs according to this.contigs
     * contig inner edge and 5' & 3' end
     * class: contig-inner-edge, contig-end-node, contig-end-node-box
     */
    renderContigs() {
      var _this = this;
      this.contigs.forEach( function(contig) {

        var c = {
          id: contig[0],
          // seq: contig[1],
          length: Number(contig[2].slice(5)), // TODO: parse CIGAR, "LN:i:81568"
        }

        var current_contig_center = cy.$( `#${c.id}` );
        var pos = current_contig_center.position();

        cy.remove( current_contig_center );

        cy.add( _this.makeContig(c, pos) );

        // update current_contig on 'tap' event
        var updateCurrentContig = function() {
          _this.current_selection.current_contig = contig;
          _this.current_selection.current_link = null;
          // send update to SidePanel for showing current_selection
          EventBus.$emit( 'currentSelectionUpdated', _this.current_selection.current_contig, 'contig');
        }
        cy.$(`#${c.id}-5-3`).on( 'tap', updateCurrentContig );
        cy.$(`#${c.id}-5-3-box`).on( 'tap', updateCurrentContig );

        var removeTickPointer = function() {
          cy.$(`#tick-pointer-5`).remove();
          cy.$(`#tick-pointer-3`).remove();
        };
        cy.$(`#${c.id}-5-3-box`).on( 'dragfree', removeTickPointer );
        cy.$(`#${c.id}-5-3-box`).on( 'drag', function() {
          removeTickPointer();
          var ruler_tick_pointer_pos = {
            x_5: cy.$(`#${c.id}-5`).renderedPosition().x,
            x_3: cy.$(`#${c.id}-3`).renderedPosition().x,
            y: _this.ruler_render_start_pos.y
          };
          cy.add( [
            {
              data: { id: 'tick-pointer-5' },
              renderedPosition: { x: ruler_tick_pointer_pos.x_5, y: ruler_tick_pointer_pos.y },
              classes: 'ruler-tick-pointer'
            },
            {
              data: { id: 'tick-pointer-3' },
              renderedPosition: { x: ruler_tick_pointer_pos.x_3, y: ruler_tick_pointer_pos.y },
              classes: 'ruler-tick-pointer'
            },
          ] );
        } );

      });
    },

    /**
     * render links among contigs according to this.links
     * class: contig-link_edge
     */
    renderLinks() {
      var _this = this;

      this.links.forEach( function(l) {
        var source = l[0];
        var target = l[2];
        var line_color = '#006666';
        var control_point_distances, control_point_weights;
        var cigar = l[4];
        var use_class = 'contig-link-edge';

        // break forEach if a link's source or end not in current this.contigs
        if ( !_this.contig_ids.includes( (source, target) ) ){
          return
        }

        // self loop if source === target
        var is_self_loop = ( source === target );
        if (l[1] === '+') {
          source = `${source}-3`;
        } else if (l[1] === '-') {
          source = `${source}-5`;
        }
        if (l[3] === '+') {
          target = `${target}-5`;
        } else if (l[3] === '-') {
          target = `${target}-3`;
        }
        // deal with edge duplication
        if ( !cy.$(`#${source}-${target}`).length && !cy.$(`#${target}-${source}`).length ) {

          if (is_self_loop) {
            var delta_x = cy.$(`#${target}`).position().x - cy.$(`#${source}`).position().x;
            control_point_distances = [ Math.abs(delta_x), Math.abs(delta_x) ].map(
              n => -0.5 * n
            );
            control_point_weights = [-1, 2];
          } else {
            // eslint-disable-next-line
            var delta_x = cy.$(`#${target}`).position().x - cy.$(`#${source}`).position().x;
            var delta_y = cy.$(`#${target}`).position().y - cy.$(`#${source}`).position().y;

            var delta_x_rate = (delta_x === 0) ? 1 : Math.abs(delta_x) / delta_x ;
            var delta_y_rate = (delta_y === 0) ? 1 : Math.abs(delta_y) / delta_y ;

            // TODO: apply multiple control points, freedom bezier link lines
            control_point_distances = [ Math.abs(delta_x) ].map(
              n => n * delta_y_rate * delta_x_rate * 0.3
            );
            control_point_weights = [0.5, 0.5];
          }

          cy.add({
            data: {
              id: `${source}-${target}`,
              source: source,
              target: target,
              line_color: line_color,
              control_point_distances: control_point_distances,
              control_point_weights: control_point_weights,
              cigar: cigar
            },
            classes: use_class,
          });
        } // end of if: remove edge duplication

        // update current_link on 'tap' event
        cy.$(`#${source}-${target}`).on( 'tap', function() {
          _this.current_selection.current_link = l;
          _this.current_selection.current_contig = null;
          // send to SidePanel for showing current_selection
          EventBus.$emit( 'currentSelectionUpdated', _this.current_selection.current_link, 'link');
        } );

      }); // end of forEach link
    },

    /**
     * load and render ruler. 
     * execute while init and update
     */
    renderRuler() {
      var _this = this;

      // calculate ruler rates
      // actual_length, logic_length, rendered_length
      // console.log( contig_lens )
      var shortest_contig_index = this.contig_lens.indexOf( this.MIN_CONTIG_LEN );
      var shortest_contig_id = this.contigs[shortest_contig_index][0];
      var shortest_contig = {
        id: shortest_contig_id,
        actual_length: this.MIN_CONTIG_LEN, // [100k ~ 200k]
        logic_length: cy.$( `#${shortest_contig_id}-3` ).position().x - cy.$( `#${shortest_contig_id}-5` ).position().x, // [3x2 ~ 25x2]
        rendered_length: cy.$( `#${shortest_contig_id}-3` ).renderedPosition().x - cy.$( `#${shortest_contig_id}-5` ).renderedPosition().x // pixel
      };

      var longest_contig_index = this.contig_lens.indexOf( this.MAX_CONTIG_LEN );
      var longest_contig_id = this.contigs[longest_contig_index][0];
      var longest_contig = {
        id: longest_contig_id,
        actual_length: this.MAX_CONTIG_LEN, // [100k ~ 200k]
        logic_length: cy.$( `#${longest_contig_id}-3` ).position().x - cy.$( `#${longest_contig_id}-5` ).position().x, // [3x2 ~ 25x2]
        rendered_length: cy.$( `#${longest_contig_id}-3` ).renderedPosition().x - cy.$( `#${longest_contig_id}-5` ).renderedPosition().x // pixel
      };

      for ( var t = 0; t < 71; t++ ) {
        // TODO make Label number more reasonable
        var toLabel = function(t) {
          if ( t == 0 ) { return '0'; }
          var result = _this.fitRange(
              shortest_contig.rendered_length * t,
              [ shortest_contig.rendered_length, longest_contig.rendered_length ],
              [ _this.MIN_CONTIG_LEN, _this.MAX_CONTIG_LEN ]
            );
          return ( result <= 1000.0 ) ? result : d3.format('.0f')( result / 1000.0 ) + 'K';
        };
        cy.add( [
            {
              data: { id: `ruler-tick-${t}`, name: toLabel(t) },
              renderedPosition: { x: _this.ruler_render_start_pos.x + shortest_contig.rendered_length * t, y: _this.ruler_render_start_pos.y},
              pannable: false,
              grabbable: false, 
              classes: ( t % 5 == 0 ) ? 'ruler-tick-large' : 'ruler-tick'
            },
          ] );

      }

      // fix y coordinate while panning(or zooming)
      cy.on('pan', function() {
        for ( var t = 0; t < 71; t++ ) {
          var x = cy.$(`#ruler-tick-${t}`).renderedPosition().x;
          cy.$(`#ruler-tick-${t}`).renderedPosition({
            x: x, y: 50
          })
        }
      });

    }, // end of renderRuler()

    /**
     * adjust cytoscape viewport, pan, etc.
     */
    cyAdjust() {
      cy.viewport({
        // zoom: 3.5,
        pan: { x: 0 }
      });
      cy.minZoom(1);
      cy.maxZoom(10);
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
     * make a contig Object for Cytoscape to render
     * @param {Object} contig { id, seq, length(actual_length) }
     * @param {Object} pos { x, y }
     * @return {Array} [ contig-end-node-box, 5-end, 3-end, contig_inner_edge ]
     */
    makeContig(contig, pos) {
      return [
        {
          data: { id: `${contig.id}-5-3-box`, name: contig.id },
          classes: 'contig-end-node-box'
        },
        {
          data: { id: `${contig.id}-5`, name: '5\'', parent: `${contig.id}-5-3-box` },
          position: { x: pos.x - this.displayLength(contig.length), y: pos.y },
          classes: 'contig-end-node'
        },
        {
          data: { id: `${contig.id}-3`, name: '3\'', parent: `${contig.id}-5-3-box` },
          position: { x: pos.x + this.displayLength(contig.length), y: pos.y },
          classes: 'contig-end-node'
        },
        {
          data: { 
            id: `${contig.id}-5-3`, 
            source: `${contig.id}-5`, 
            target: `${contig.id}-3`, 
            // sequence: contig.seq, 
            length: contig.length 
          },
          classes: 'contig-inner-edge',
        }
      ];
    },

  }
}

</script>

<style scoped>
  #cy {
    height: 100%;
    width: 100%;
    position: absolute;
    left: 0;
    top: 0;
  }
</style>
