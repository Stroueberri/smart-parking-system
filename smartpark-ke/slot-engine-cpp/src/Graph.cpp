#include "Graph.h"
#include <algorithm>

ParkingGraph::ParkingGraph() {}

ParkingGraph::~ParkingGraph() {}

void ParkingGraph::addNode(int nodeId, const std::string& label) {
    if (adjList.find(nodeId) == adjList.end()) {
        adjList[nodeId] = std::vector<Edge>();
    }
    nodeLabels[nodeId] = label;
}

void ParkingGraph::addEdge(int u, int v, double weight) {
    // Add forward edge
    adjList[u].push_back(Edge{v, weight});
    // Add reverse edge for two-way lane navigation
    adjList[v].push_back(Edge{u, weight});
}

PathResult ParkingGraph::dijkstra(int startNode) const {
    PathResult result;
    const double INF = std::numeric_limits<double>::infinity();

    for (const auto& pair : adjList) {
        result.distances[pair.first] = INF;
    }

    if (result.distances.find(startNode) == result.distances.end()) {
        result.distances[startNode] = 0.0;
    } else {
        result.distances[startNode] = 0.0;
    }

    // Min-priority queue storing pairs: (distance, nodeId)
    typedef std::pair<double, int> DistNode;
    std::priority_queue<DistNode, std::vector<DistNode>, std::greater<DistNode>> pq;

    pq.push({0.0, startNode});

    while (!pq.empty()) {
        auto [currentDist, u] = pq.top();
        pq.pop();

        if (currentDist > result.distances[u]) {
            continue;
        }

        auto it = adjList.find(u);
        if (it != adjList.end()) {
            for (const auto& edge : it->second) {
                int v = edge.targetNode;
                double weight = edge.weight;

                if (result.distances[u] + weight < result.distances[v]) {
                    result.distances[v] = result.distances[u] + weight;
                    result.predecessors[v] = u;
                    pq.push({result.distances[v], v});
                }
            }
        }
    }

    return result;
}

std::vector<int> ParkingGraph::reconstructPath(const std::unordered_map<int, int>& predecessors, int targetNode) const {
    std::vector<int> path;
    int curr = targetNode;
    path.push_back(curr);

    while (predecessors.find(curr) != predecessors.end()) {
        curr = predecessors.at(curr);
        path.push_back(curr);
    }

    std::reverse(path.begin(), path.end());
    return path;
}

std::string ParkingGraph::getNodeLabel(int nodeId) const {
    auto it = nodeLabels.find(nodeId);
    if (it != nodeLabels.end()) {
        return it->second;
    }
    return "Node_" + std::to_string(nodeId);
}

size_t ParkingGraph::nodeCount() const {
    return adjList.size();
}
