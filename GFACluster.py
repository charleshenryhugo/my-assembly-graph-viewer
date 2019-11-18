import sys
import os
import json
import networkx as nx
from networkx.algorithms import community
import pdb

# contigs(links) data directory
data_dir = os.path.join( os.getcwd(), 'data' )

# assembler name
assembler = 'unknown'

# dictionary for contigs
# { 
#   'contig_01': {sequence: 'ATCG', 'length': 'LN:i:12345'},
#   'contig_02': {sequence: 'CGAT', 'length': 'LN:i:67890'},
#   ...
# }
contigs_dict = dict()

# graph structure for cluster & community the big graph
MG = nx.MultiGraph()

# overview description of graph clusters
clusters_overview = []

# make contigs_dict and Multi Graph from GFA file
# construct contigs_dict
# gfa1 supported; not supporting gfa2 yet
def parse_gfa(filename):
    with open(filename) as f:
        for line in f:
            eles = line.split()
            if eles[0] == 'S':
                contigs_dict[eles[1]] = {
                    'sequence': eles[2],
                    'length': eles[3]
                }
            if eles[0] == 'L':
                MG.add_edge(eles[1], eles[3], desc = eles[1:])

# write json_data to a js file
def write_json(json_data, outfile_name):
    with open(outfile_name, 'w', encoding='utf-8') as outfile:
        json.dump(json_data, outfile, ensure_ascii=False, indent=2)

    # print('finished writing {filename}'.format(filename=outfile_name))

# recursively decompose a multi graph to small communities (nodes <= 50)
# under a certain cluster directory: cur_work_dir ( e.g. ./data/miniasam_cluster_10/ )
# create sub directories recursively
def decompose_multi_graph_communities(cur_work_dir, cluster_id, community_id, multi_graph, expansion_edges):

    # append communities tree to current cluster_id
    community_layers = cur_work_dir[ len(data_dir)+1: ].split('/')[1:] # ['29','7','1',...'4']
    target = clusters_overview[cluster_id]['communities']
    for layer in community_layers:
        target.setdefault( layer, {
            'community_id': int(layer),
            'community_dir': cur_work_dir,
            'size': len( multi_graph ),
            'communities': {},
            'expansion_edges': expansion_edges
        })
        target = target[layer]['communities']

    if len( multi_graph ) <= 50:
        contigs_collection = [
            [
                contig_id,
                contigs_dict[contig_id]['sequence'],
                contigs_dict[contig_id]['length']
            ]
            for contig_id in multi_graph.nodes()
        ]

        links_collection = [
            link[2]
            #for link in MG.edges( multi_graph.nodes(), data = 'desc')
            for link in multi_graph.edges.data('desc')
        ]

        contigs_outfile_name = \
            '{cur_work_dir}/contigs.json'.format(cur_work_dir=cur_work_dir)
        write_json(contigs_collection, contigs_outfile_name)

        links_outfile_name = \
            '{cur_work_dir}/links.json'.format(cur_work_dir=cur_work_dir)
        write_json(links_collection, links_outfile_name)

    else:
        nodes_communities = list( community.greedy_modularity_communities(multi_graph) )
        for c_id, nodes_community in enumerate( nodes_communities ):
            community_dir = '{cwd}/{c_id}'.format(cwd=cur_work_dir, c_id=c_id)
            if not os.path.exists(community_dir):
                os.makedirs(community_dir)

            # find the linkages with other communities in the same layer
            shared_expansion_edges = dict()
            tempG = nx.MultiGraph( multi_graph.edges( nodes_community ) )
            multi_graph_this_expansion = multi_graph.subgraph( tempG.nodes )
            multi_graph_this = multi_graph.subgraph( nodes_community )
            expansion_edges_this = set([ tuple(data[2]) for data in multi_graph_this_expansion.edges.data('desc') ]) -\
                set([ tuple(data[2]) for data in multi_graph_this.edges.data('desc') ])

            for X, other_nodes_community in enumerate( nodes_communities ):
                if c_id == X:
                    continue
                try:
                    target = clusters_overview[cluster_id]['communities']
                    for layer in community_layers[:-1]:
                        target = target[layer]['communities']
                    shared_expansion_edges[X] = target[str(X)]['expansion_edges'][c_id]
                except:
                    tempG = nx.MultiGraph( multi_graph.edges( other_nodes_community ) )
                    multi_graph_X_expansion = multi_graph.subgraph( tempG.nodes )
                    multi_graph_X = multi_graph.subgraph( other_nodes_community )
                    expansion_edges_X = set([ tuple(data[2]) for data in multi_graph_X_expansion.edges.data('desc') ]) -\
                        set([ tuple(data[2]) for data in multi_graph_X.edges.data('desc') ])
                    if len(expansion_edges_X & expansion_edges_this) > 0:
                        shared_expansion_edges[X] = list( expansion_edges_X & expansion_edges_this )

            decompose_multi_graph_communities( community_dir, cluster_id, c_id, multi_graph.subgraph( nodes_community ), shared_expansion_edges )



def main(argv):
    # parse GFA file
    # construct contigs_dict and MG
    if not argv[0] is None:
        parse_gfa( str( argv[0]) )

    # set assembler name
    if not argv[1] is None:
        assembler = str( argv[1] )

    for cluster_id, contigs_cluster_graph in enumerate( nx.connected_component_subgraphs(MG) ):

        # make directory for current cluster id
        cluster_dir = '{data_dir}/{assembler}_cluster_{id}'.format(data_dir=data_dir, assembler=assembler, id=cluster_id)
        if not os.path.exists(cluster_dir):
            os.makedirs(cluster_dir)

        # append to clusters_overview: []
        # clusters_overview[cluster_id] = { 'cluster_id': cluster_id, ... }
        clusters_overview.append({
            'cluster_id': cluster_id,
            'cluster_dir': cluster_dir,
            'size': len( contigs_cluster_graph ),
            'communities': {}
        })

        # write cluster to json if contigs number <= 50
        if len(contigs_cluster_graph) <= 50:

            contigs_collection = [
                [
                    contig_id,
                    contigs_dict[contig_id]['sequence'],
                    contigs_dict[contig_id]['length']
                ]
                for contig_id in contigs_cluster_graph.nodes()
            ]

            links_collection = [
                link[2]
                for link in contigs_cluster_graph.edges.data('desc')
            ]

            # write json to file
            contigs_outfile_name = \
                '{cluster_dir}/contigs.json'.format(cluster_dir=cluster_dir)
            write_json(contigs_collection, contigs_outfile_name)

            links_outfile_name = \
                '{cluster_dir}/links.json'.format(cluster_dir=cluster_dir)
            write_json(links_collection, links_outfile_name)

        else:
            # cluster size > 50
            # recursively calculate communities
            # under the cluster folder: ./data/miniasam_cluster_10/
            decompose_multi_graph_communities(cluster_dir, cluster_id, -1, contigs_cluster_graph, -1)


    # write isolated contigs data
    # e.g. miniasm_isolated_contigs.json
    for node in MG.nodes():
        contigs_dict.pop(node)

    isolated_contigs_collection = [
        [
            contig[0], contig[1]['sequence'], contig[1]['length']
        ]
        for contig in contigs_dict.items()
    ]

    isolated_contigs_cluster_dir = '{data_dir}/isolated_contigs_cluster'.format(data_dir=data_dir)
    if not os.path.exists(isolated_contigs_cluster_dir):
        os.makedirs(isolated_contigs_cluster_dir)

    contigs_outfile_name = '{isolated_contigs_cluster_dir}/contigs.json'.format(isolated_contigs_cluster_dir=isolated_contigs_cluster_dir)
    links_outfile_name = '{isolated_contigs_cluster_dir}/links.json'.format(isolated_contigs_cluster_dir=isolated_contigs_cluster_dir)
    write_json(isolated_contigs_collection, contigs_outfile_name)
    write_json([], links_outfile_name)

    # append isolated_contigs to clusters_overview: [...]
    clusters_overview.append({
        'cluster_id': len( clusters_overview ),
        "isolated_contigs_cluster": True,
        'cluster_dir': isolated_contigs_cluster_dir,
        'size': len( isolated_contigs_collection ),
        'communities': {}
    })
    # write overview.json
    write_json(clusters_overview, '{data_dir}/overview.json'.format(data_dir=data_dir) )



if __name__ == '__main__':
    main(sys.argv[1:])