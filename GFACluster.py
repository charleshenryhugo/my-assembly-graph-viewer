import sys
import os
import json
import networkx as nx
from networkx.algorithms import community

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

# make contigs_dict and Multi Graph from GFA file
# construct contigs_dict
# gfa1 ok, not for gfa2 yet
def parse_gfa(filename):
    # TODO use gfapy
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

    print('finished writing {filename}'.format(filename=outfile_name))

# recursively decompose a multi graph to small communities (nodes <= 50)
# under a certain cluster directory: cur_work_dir ( e.g. ./data/miniasam_cluster_10/ )
# create sub directories recursively
def decompose_multi_graph_communities(cur_work_dir, community_id, multi_graph):
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
            for link in MG.edges( multi_graph.nodes(), data = 'desc')
        ]

        contigs_outfile_name = \
            '{cur_work_dir}/contigs_{community_id}.json'.format(cur_work_dir=cur_work_dir, community_id=community_id)
        write_json(contigs_collection, contigs_outfile_name)
        
        links_outfile_name = \
            '{cur_work_dir}/links_{community_id}.json'.format(cur_work_dir=cur_work_dir, community_id=community_id)
        write_json(links_collection, links_outfile_name)

    else:
        for c_id, nodes_community in enumerate( community.greedy_modularity_communities(multi_graph) ):
            community_dir = '{cwd}/{c_id}'.format(cwd=cur_work_dir, c_id=c_id)
            if not os.path.exists(community_dir):
                os.makedirs(community_dir)

            edges_community = multi_graph.edges( nodes_community )
            decompose_multi_graph_communities( community_dir, c_id, nx.MultiGraph(edges_community) )


def main(argv):
    # parse GFA file
    # construct contigs_dict and MG
    if not argv[0] is None:
        parse_gfa( str(argv[0]) )

    # set assembler name
    if not argv[1] is None:
        assembler = str( argv[1] )

    for cluster_id, contigs_cluster_graph in enumerate(nx.connected_component_subgraphs(MG)):

        # write cluster to js if contigs number <= 50
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
                '{data_dir}/{assembler}_contigs_cluster_{id}.json'.format(data_dir=data_dir, assembler=assembler, id=cluster_id)
            write_json(contigs_collection, contigs_outfile_name)

            links_outfile_name = \
                '{data_dir}/{assembler}_links_cluster_{id}.json'.format(data_dir=data_dir, assembler=assembler, id=cluster_id)
            write_json(links_collection, links_outfile_name)

        else:
            # make directory for current cluster id
            cluster_dir = '{data_dir}/{assembler}_cluster_{id}'.format(data_dir=data_dir, assembler=assembler, id=cluster_id)
            if not os.path.exists(cluster_dir):
                os.makedirs(cluster_dir)
            
            # recursively calculate communities
            # under the cluster folder: ./data/miniasam_cluster_10/
            decompose_multi_graph_communities(cluster_dir, -1, contigs_cluster_graph)


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

    outfile_name = '{data_dir}/{assembler}_isolated_contigs.json'.format(data_dir=data_dir, assembler=assembler)
    write_json(isolated_contigs_collection, outfile_name)



if __name__ == '__main__':
    main(sys.argv[1:])