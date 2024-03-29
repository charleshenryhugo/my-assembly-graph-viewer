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

    // css for a contig's 5' or 3' end
    {
        selector: '.contig-end-node',
        style: {
            'background-color': '#ffb266',
            'width': 1,
            'height': 1,
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
            'line-color': '#87ceeb',
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
            'width': 0.2,
            'line-color': '#ffb266',
            'curve-style': 'unbundled-bezier',
            'control-point-distances': 'data(control_point_distances)',
            'control-point-weights': 'data(control_point_weights)',
            'target-arrow-color': '#ffb266',
            'target-arrow-shape': 'vee',
            'arrow-scale': 0.2,
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
            'font-size': 3
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