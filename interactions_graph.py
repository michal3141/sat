#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import matplotlib.pyplot as plt 
import numpy as np

from analyzer import FormulaAnalyzer
from collections import defaultdict, Counter
from graphviz import Graph as GGraph, Digraph
from model import Model
from itertools import permutations

from graph_tool.all import *


styles = { 
    'graph': {
        'label': 'Graph',
        'fontsize': '12',
        'fontcolor': 'white',
        'bgcolor': '#888888',
        'overlap': 'prism',
        'outputorder': 'edgesfirst'
        # 'rankdir': 'BT'
    },  
    'nodes': {
        'fontname': 'Helvetica',
        'shape': 'hexagon',
        'fontcolor': 'white',
        'color': 'white',
        'style': 'filled',
        'fillcolor': '#006699',
    },  
    'edges': {
        'color': 'black',
        'arrowhead': 'open',
        'fontname': 'Courier',
        'fontsize': '12',
        'fontcolor': 'white',
    }   
}

def _apply_styles(graph, styles):
    graph.graph_attr.update(
        ('graph' in styles and styles['graph']) or {}
    )
    graph.node_attr.update(
        ('nodes' in styles and styles['nodes']) or {}
    )
    graph.edge_attr.update(
        ('edges' in styles and styles['edges']) or {}
    )
    return graph


# Creating interaction graph between variables using clauses
def create_interactions_graph(clauses, f):
    dot = GGraph(comment='Interactions graph', engine='sfdp')
    seen_vars = set()
    edges_between_vars = defaultdict(int)

    for clause in clauses:
        for lit in clause:
            var = f(lit)
            if var not in seen_vars:
                seen_vars.add(var)
                dot.node(str(var), label=str(var))
    for clause in clauses:
        l = len(clause)
        for i in xrange(l):
            for j in xrange(i+1, l):
                edges_between_vars[(str(f(clause[i])), str(f(clause[j])))] += 1

    for interacting_vars, weight in edges_between_vars.iteritems():
        dot.edge(interacting_vars[0], interacting_vars[1], weight=str(weight))

    print edges_between_vars

    dot = _apply_styles(dot, styles)
    # print dot.source
    dot.render(os.path.join('images', 'interactions_graph.gv'), view=True)   

# Creating implications graph
def create_implications_graph(clauses):
    dot = Digraph(comment='Implications graph', engine='sfdp')
    seen_vars = set()
    edges = set()

    # for clause in clauses:
    #     for lit in clause:
    #         if lit not in seen_vars:
    #             seen_vars.add(lit)
    #             dot.node(str(lit), label=str(lit))    

    for clause in clauses:
        for perm in permutations(clause):
            l = len(perm)
            for i in xrange(l-2):
                edges.add((-perm[i], -perm[i+1]))
            edges.add((-perm[l-2], perm[l-1]))

    for (head, tail) in edges:
        dot.edge(str(head).replace('-','~'), str(tail).replace('-', '~'))

    dot = _apply_styles(dot, styles)
    dot.render(os.path.join('images', 'implications_graph.gv'), view=True)

# If two clauses have conflicting literals then there is an edge between those clauses
def create_conflicts_graph(clauses):
    dot = GGraph(comment='Conflicts graph', engine='sfdp')

    for i in xrange(len(clauses)):
        dot.node(str(i), label=str(i))

    for i in xrange(len(clauses)):
        for j in xrange(i+1, len(clauses)):
            clause_i = clauses[i]
            clause_j = clauses[j]
            edge_labels = []
            for lit in clause_i:
                if -lit in clause_j:
                    var = abs(lit)
                    edge_labels.append(str(var))
            if len(edge_labels) > 0:
                dot.edge(str(i), str(j), label=','.join(edge_labels)) 

    dot = _apply_styles(dot, styles)
    dot.render(os.path.join('images', 'conflicts_graph.gv'), view=True)

# Creating interactions graphs using graph-tool
def create_interactions_graph_gt(clauses, f):
    ug = Graph(directed=False)
    labels = ug.new_vertex_property("string")
    e_weights = ug.new_edge_property("double")

    vertices = {}
    edges_between_vars = defaultdict(int)

    for clause in clauses:
        for lit in clause:
            var = f(lit)
            if var not in vertices:
                v = ug.add_vertex()
                vertices[var] = v
                labels[v] = str(var)

    for clause in clauses:
        l = len(clause)
        for i in xrange(l):
            for j in xrange(i+1, l):
                f_clause_i = f(clause[i])
                f_clause_j = f(clause[j])
                mini = min(f_clause_i, f_clause_j)
                maxi = max(f_clause_i, f_clause_j)
                edges_between_vars[(mini, maxi)] += 1

    for interacting_vars, weight in edges_between_vars.iteritems():
        print interacting_vars, weight
        e = ug.add_edge(vertices[interacting_vars[0]], vertices[interacting_vars[1]])
        e_weights[e] = weight

    print 'Planarity:', is_planar(ug) 
    graph_draw(ug, vertex_text=labels, edge_pen_width = e_weights, vertex_font_size=18, output_size=(800, 800), output="images/interactions_graph.png")


def main():
    n = sys.argv[1]
    f = Model.parse_dimacs('data/%s.dimacs' % n)
    f.unit_propagate()

    # create_interactions_graph(f.clauses, abs)
    # create_interactions_graph(f.clauses, lambda x: x)

    # create_interactions_graph_gt(f.clauses, abs)
    # create_interactions_graph_gt(f.clauses, lambda x: x)

    create_conflicts_graph(f.clauses)

    # create_implications_graph([[1, 2, 3], [1, 2, -3], [1, -2, 3], [1, -2, -3], [-1, 2, 3], [-1, 2, -3], [-1, -2, 3]])

if __name__ == '__main__':
    main()