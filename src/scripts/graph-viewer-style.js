// This is the css for cytoscape object
module.exports = [
    // normal node css
    {
        selector: 'node',
        style: {
            'width': 5,
            'height': 5,
            'label': 'data(id)',
            'font-size': 2
        }
    },
    // normal edge css
    {
        selector: 'edge',
        style: {
            'width': 0.5,
        }
    },

    // css for a contig's box (parent or compound node)
    {
        selector: '.contig-end-node-box',
        style: {
            'opacity': 0.8,
            // 'label': 'data(name)',
            'label': '',
            'border-width': 0.1,
            'padding': 3,
        }
    },

    // css for a contig's 5' or 3' end
    {
        selector: '.contig-end-node',
        style: {
            'background-color': '#ffb266',
            'width': 2,
            'height': 2,
            'label': 'data(name)',
            'font-size': 1,
            'text-valign': 'center',
            'text-halign': 'center',
        }
    },
    // css for a contig rectangle( a bold edge )
    {
        selector: '.contig-inner-edge',
        style: {
            'width': 5,
            'line-color': '#00cc66',
            'label': 'data(name)', // 'data(length)',
            'font-size': 2,
            'text-margin-y': 4,
            'text-wrap': 'ellipsis',
            'text-max-width': 50,
        }
    },
    // css for a linkage edge between 2 contigs
    {
        selector: '.contig-link-edge',
        style: {
            'width': 0.1,
            'line-color': '#006666',
            'curve-style': 'unbundled-bezier',
            'control-point-distances': 'data(control_point_distances)',
            'control-point-weights': 'data(control_point_weights)',
            // 'target-arrow-color': '#006666',
            // 'target-arrow-shape': 'triangle',
            // 'arrow-scale': 0.1,
        }
    },
    // css for highlighted contigs
    {
        selector: '.highlighted-contig-inner-edge',
        style: {
            'line-color': '#ffb266',
        }
    },

    // css for ruler tick
    {
        selector: '.ruler-tick',
        style: {
            'shape': 'rectangle',
            'width': 0.5,
            'height': 1,
            'label': '',
        }
    },
    // css for ruler tick large
    {
        selector: '.ruler-tick-large',
        style: {
            'shape': 'diamond',
            'width': 0.5,
            'height': 5,
            'background-color': '#006666',
            'label': 'data(name)',
            'font-size': 5
        }
    },
    // css for ruler tick pointer
    {
        selector: '.ruler-tick-pointer',
        style: {
            'shape': 'ellipse',
            'width': 1,
            'height': 1,
            'background-color': '#ffb266',
            'label': ''
        }
    },
];