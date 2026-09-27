#ifndef GRAPH_H
#define GRAPH_H

#include <vector>
#include <string>
#include <unordered_map>
#include <queue>
#include <limits>

/**
 * @struct Edge
 * @brief Represents a directed/undirected weighted path between two lot nodes.
 */
struct Edge {
    int targetNode;
    double weight; ///< Distance in meters
};

/**
 * @struct PathResult
 * @brief Output of Dijkstra calculation containing distances and path sequence.
 */
struct PathResult {
    std::unordered_map<int, double> distances;
    std::unordered_map<int, int> predecessors;
};

/**
 * @class ParkingGraph
 * @brief Weighted Graph modeling parking lot lanes, ramps, junctions, and slots.
 *
 * Implements Dijkstra's algorithm to compute shortest paths across multi-floor
 * and multi-zone layouts from entry gates to parking bays.
 *
 * Time Complexity:
 *  - Dijkstra: O((V + E) log V) using priority queue
 *  - Space Complexity: O(V + E)
 */
class ParkingGraph {
private:
    std::unordered_map<int, std::vector<Edge>> adjList;
    std::unordered_map<int, std::string> nodeLabels;

public:
    ParkingGraph();
    ~ParkingGraph();

    /**
     * @brief Adds a node (junction, entrance, ramp, or slot) to the graph.
     * @param nodeId Unique numeric ID.
     * @param label Human-readable label (e.g. "MAIN_ENTRANCE", "RAMP_F1", "SLOT_A1").
     */
    void addNode(int nodeId, const std::string& label);

    /**
     * @brief Adds a bidirectional driving path between two nodes.
     * @param u Source node ID.
     * @param v Destination node ID.
     * @param weight Distance in meters.
     */
    void addEdge(int u, int v, double weight);

    /**
     * @brief Computes shortest paths from startNode to all reachable nodes using Dijkstra's algorithm.
     * @param startNode Entrance node ID.
     * @return PathResult containing shortest distance map and predecessor pointers.
     * @complexity O((V + E) log V)
     */
    PathResult dijkstra(int startNode) const;

    /**
     * @brief Reconstructs the exact sequence of node IDs along the shortest path.
     * @param predecessors Map of node -> previous node from Dijkstra.
     * @param targetNode Destination slot node ID.
     * @return std::vector<int> Path sequence from source to destination.
     */
    std::vector<int> reconstructPath(const std::unordered_map<int, int>& predecessors, int targetNode) const;

    /**
     * @brief Returns label for a given node.
     */
    std::string getNodeLabel(int nodeId) const;

    /**
     * @brief Returns total number of vertices in graph.
     */
    size_t nodeCount() const;
};

#endif // GRAPH_H
