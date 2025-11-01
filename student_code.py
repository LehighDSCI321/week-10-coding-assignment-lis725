"""VersatileDigraph"""
import importlib
from typing import Iterator, Tuple
from collections import deque
class VersatileDigraph:
    """
    A flexible directed graph.

    Core structures:
      - self._nodes: node_id -> node_value
      - self._out:   start_id -> {
                        "by_end":  end_id -> (weight, name),
                        "by_name": name   -> end_id,
                        "ctr":     auto-name counter (int)
                     }
    Invariants:
      - node_id is a string (coerced with str()).
      - At most one edge for a (start, end) pair.
      - Edge names are unique per start node.
    """

    def __init__(self):
        self._nodes = {}
        self._out = {}

    def add_node(self, node_id, node_value=0):
        """Add or update a node. Value must be numeric (int/float) or None."""
        nid = str(node_id)
        if node_value is not None and not isinstance(node_value, (int, float)):
            raise TypeError("node_value must be numeric (int/float) or None.")
        self._nodes[nid] = float(node_value) if node_value is not None else 0.0
        if nid not in self._out:
            self._out[nid] = {"by_end": {}, "by_name": {}, "ctr": 0}


    def get_nodes(self):
        """Return a list of node ids in the graph."""
        return list(self._nodes.keys())

    def get_node_value(self, node_id):
        """Return the value for node_id; raises KeyError if missing."""
        nid = str(node_id)
        return self._nodes[nid]

    def add_edge(
        self,
        start_node_id,
        end_node_id,
        start_node_value=None,
        end_node_value=None,
        edge_name=None,
        edge_weight=0,
    ):
        """
        Add or update a directed edge start->end with optional name and weight.

        - Adds start/end nodes if missing (using provided node_values or default 0).
        - Ensures: one edge per (start, end); edge names unique per start.
        """
        s, t = str(start_node_id), str(end_node_id)

        if not isinstance(edge_weight, (int, float)):
            raise TypeError("edge_weight must be numeric (int/float).")

        if edge_weight < 0:
            raise ValueError("edge_weight cannot be negative.")

        if start_node_value is not None and not isinstance(start_node_value, (int, float)):
            raise TypeError("start_node_value must be numeric (int/float) or None.")
        if end_node_value is not None and not isinstance(end_node_value, (int, float)):
            raise TypeError("end_node_value must be numeric (int/float) or None.")

        if s not in self._nodes:
            self.add_node(s, 0 if start_node_value is None else start_node_value)
        elif start_node_value is not None:
            self._nodes[s] = float(start_node_value)

        if t not in self._nodes:
            self.add_node(t, 0 if end_node_value is None else end_node_value)
        elif end_node_value is not None:
            self._nodes[t] = float(end_node_value)

        if s not in self._out:
            self._out[s] = {"by_end": {}, "by_name": {}, "ctr": 0}

        bucket = self._out[s]
        by_end, by_name = bucket["by_end"], bucket["by_name"]

        if edge_name is None:
            name = f"e{bucket['ctr']}"
            while name in by_name:
                bucket["ctr"] += 1
                name = f"e{bucket['ctr']}"
            bucket["ctr"] += 1
        else:
            name = str(edge_name)
            if name in by_name and by_name[name] != t:
                raise ValueError("Edge name already used for a different end node.")

        if t in by_end:
            _, old_name = by_end[t]
            if edge_name is not None and name != old_name:
                if old_name in by_name:
                    del by_name[old_name]
                by_name[name] = t
                by_end[t] = (float(edge_weight), name)
            else:
                by_end[t] = (float(edge_weight), old_name)
        else:
            if name in by_name and by_name[name] != t:
                raise ValueError(
                    "Edge name from this start is already mapped to another end node."
                )
            by_name[name] = t
            by_end[t] = (float(edge_weight), name)

    def iter_edges(self) -> Iterator[Tuple[str, str, float, str]]:
        """Yield (start, end, weight, name) for every edge."""
        for s, bucket in self._out.items():
            for t, (w, name) in bucket["by_end"].items():
                yield s, t, w, name

    def get_edge_weight(self, start_node_id, end_node_id):
        """Return the weight for edge start->end; raises KeyError if not present."""
        s, t = str(start_node_id), str(end_node_id)
        weight, _name = self._out[s]["by_end"][t]
        return weight

    def print_graph(self):
        """Print nodes and edges in readable sentences."""
        for nid in sorted(self._nodes.keys()):
            print(f"Node {nid} with value {self._nodes[nid]:g}")
        for s in sorted(self._out.keys()):
            bucket = self._out[s]
            for t, (w, name) in bucket["by_end"].items():
                print(f"Edge from {s} to {t} with weight {w:g} and name {name}")

    def predecessors(self, node_id):
        """Return a list of nodes that have an edge into node_id."""
        nid = str(node_id)
        if nid not in self._nodes:
            raise KeyError(f"Unknown node: {nid}")
        return [s for s, bucket in self._out.items() if nid in bucket["by_end"]]

    def successors(self, node_id):
        """Return a list of nodes that node_id points to."""
        nid = str(node_id)
        if nid not in self._nodes:
            raise KeyError(f"Unknown node: {nid}")
        return [t for t in self._out[nid]["by_end"].keys()]

    def successor_on_edge(self, node_id, edge_name):
        """Given a start node and an edge name, return the end node of that edge."""
        nid, ename = str(node_id), str(edge_name)
        if nid not in self._nodes:
            raise KeyError(f"Unknown node: {nid}")
        try:
            return self._out[nid]["by_name"][ename]
        except KeyError as exc:
            raise KeyError(f"No edge named {ename!r} from node {nid!r}") from exc

    def in_degree(self, node_id):
        """Number of incoming edges to node_id."""
        nid = str(node_id)
        if nid not in self._nodes:
            raise KeyError(f"Unknown node: {nid}")
        return sum(1 for _s, bucket in self._out.items() if nid in bucket["by_end"])

    def out_degree(self, node_id):
        """Number of outgoing edges from node_id."""
        nid = str(node_id)
        if nid not in self._nodes:
            raise KeyError(f"Unknown node: {nid}")
        return len(self._out[nid]["by_end"])

    def plot_graph(self, filename: str = "versatile_digraph", file_format: str = "png"):
        """Render the digraph with Graphviz and return the output path."""
        try:
            gv = importlib.import_module("graphviz")
        except ImportError as exc:
            raise ImportError(
                "graphviz is required for plot_graph(); run `pip install graphviz` "
                "and ensure the Graphviz 'dot' executable is on PATH."
            ) from exc

        dot = gv.Digraph(format=file_format)
        for nid, val in self._nodes.items():
            show_val = int(val) if isinstance(val, float) and val.is_integer() else val
            dot.node(nid, f"{nid}:{show_val}")

        for s, t, w, name in self.iter_edges():
            w_lbl = int(w) if float(w).is_integer() else w
            edge_lbl = f"{name}:{w_lbl}" if name else str(w_lbl)
            dot.edge(s, t, label=edge_lbl)

        return dot.render(filename=filename, cleanup=True)

    def plot_edge_weights(self, use_names: bool = True, html_out: str = "edge_weights.html"):
        """Bokeh grouped bar chart of edge weights (main=edge name, sub=start→end)."""

        try:
            bk_plot = importlib.import_module("bokeh.plotting")
            bk_models = importlib.import_module("bokeh.models")
        except ImportError as exc:
            raise ImportError(
                "bokeh is required for plot_edge_weights(); run `pip install bokeh`."
            ) from exc

        items = []
        for s, t, w, name in self.iter_edges():
            main = name if (use_names and name) else f"{s}→{t}"
            sub = f"{s}→{t}"
            items.append(((main, sub), float(w), main, sub))

        if not items:
            raise ValueError("No edges to plot.")

        items.sort(key=lambda x: (x[0][0], x[0][1]))
        factors = [it[0] for it in items]
        weights = [it[1] for it in items]
        mains = [it[2] for it in items]
        subs = [it[3] for it in items]

        src = bk_models.ColumnDataSource(
            {"factors": factors, "weight": weights, "main": mains, "route": subs}
        )

        p = bk_plot.figure(
            x_range=bk_models.FactorRange(*factors),
            height=420,
            title="Edge Weights (grouped by edge name)",
            toolbar_location=None,
            tools="",
        )
        p.vbar(x="factors", top="weight", width=0.8, source=src)

        p.y_range.start = 0
        p.xgrid.grid_line_color = None
        p.xaxis.major_label_orientation = 0.9
        p.yaxis.axis_label = "Distance / Weight"

        p.add_tools(
            bk_models.HoverTool(
                tooltips=[("edge name", "@main"), ("route", "@route"), ("weight", "@weight{0.##}")]
            )
        )

        bk_plot.output_file(html_out, title="Edge Weights")
        bk_plot.save(p)
        bk_plot.show(p)
        return p

class SortableDigraph(VersatileDigraph):
    """Directed graph with topological sorting capability."""

    def top_sort(self):
        """Return a list of node ids in topologically sorted order (Kahn's algorithm)."""
        # Step 1: Compute in-degrees
        in_degree = {nid: 0 for nid in self._nodes}
        for _, bucket in self._out.items():
            for t in bucket["by_end"]:
                in_degree[t] += 1

        # Step 2: Start with nodes that have in-degree 0
        queue = [nid for nid, deg in in_degree.items() if deg == 0]
        sorted_nodes = []

        # Step 3: Remove nodes with in-degree 0, update neighbors
        while queue:
            current = queue.pop(0)
            sorted_nodes.append(current)
            for t in self._out[current]["by_end"]:
                in_degree[t] -= 1
                if in_degree[t] == 0:
                    queue.append(t)

        # Step 4: Check for cycles
        if len(sorted_nodes) != len(self._nodes):
            raise ValueError("Graph contains a cycle — topological sort not possible.")

        return sorted_nodes

class TraversableDigraph(SortableDigraph):
    """Adds DFS and BFS traversals that DO NOT yield the start node (per tests)."""

    def dfs(self, start):
        """Yield nodes in depth-first order starting from `start`, excluding `start` itself.
        The traversal is deterministic because neighbors are visited in sorted order.
        """
        start = str(start)
        visited = {start}

        def _dfs(u):
            for v in sorted(self._out[u]["by_end"]):
                if v not in visited:
                    visited.add(v)
                    yield v
                    yield from _dfs(v)

        return _dfs(start)

    def bfs(self, start):
        """Yield nodes in breadth-first order starting from `start`, excluding `start` itself.
        Uses a deque for efficiency. Neighbors are visited in sorted order to keep output stable.
        """
        start = str(start)
        visited = {start}
        q = deque([start])

        while q:
            u = q.popleft()
            for v in sorted(self._out[u]["by_end"]):
                if v not in visited:
                    visited.add(v)
                    q.append(v)
                    yield v

class DAG(TraversableDigraph):
    """DAG that forbids edges which would create a cycle."""

    def add_edge(
        self,
        start_node_id,
        end_node_id,
        start_node_value=None,
        end_node_value=None,
        edge_name=None,
        edge_weight=0,
    ):
        s = str(start_node_id)
        t = str(end_node_id)

        # If t already reaches s, then adding s -> t would create a cycle
        if t in self._nodes:
            stack = [t]
            seen = {t}
            while stack:
                u = stack.pop()
                if u == s:
                    raise ValueError(f"Adding edge {s} -> {t} would create a cycle.")
                for v in self._out[u]["by_end"]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)

        super().add_edge(s, t, start_node_value, end_node_value,
                         edge_name=edge_name, edge_weight=edge_weight)
