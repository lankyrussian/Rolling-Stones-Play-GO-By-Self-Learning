#include <stdio.h>
#include <vector>
#include "AStar.h"

class PathFinder
{
public:
	PathFinder();
	~PathFinder();

	void initializeAndExpand(int newMap[25]);
	void putNewStone(int newIndex, int playerColor);
	void removeStone(int index);


private:
	int map[25];
	std::vector<int> expandedMap;
	AStar::Generator astarObj;
	std::vector<int> pathCooridnates;

};

