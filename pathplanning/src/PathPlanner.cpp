#include "PathPlanner.h"

PathFinder::PathFinder()
{}

PathFinder::~PathFinder()
{}

void PathFinder::initializeAndExpand(int newMap[25])
{
	//initialize or subscribe to map 

	astarObj.setWorldSize({ 13,9 });


	for (int i = 0; i < 25; i++)
		map[i] = newMap[i];

	expandedMap.clear();
	for (int i = 0; i < 24; i++)
	{
		expandedMap.push_back(-1);
	}
	for (int i = 0; i < 5; i++)
	{
		expandedMap.push_back(-1);
		expandedMap.push_back(-1);
		expandedMap.push_back(map[(5*i)]);
		expandedMap.push_back(-1);
		expandedMap.push_back(map[(5 * i) +1]);
		expandedMap.push_back(-1);
		expandedMap.push_back(map[(5 * i) +2]);
		expandedMap.push_back(-1);
		expandedMap.push_back(map[(5 * i) +3]);
		expandedMap.push_back(-1);
		expandedMap.push_back(map[(5 * i) +4]);
		expandedMap.push_back(-1);
		expandedMap.push_back(-1);
	}
	for (int i = 0; i < 24; i++)
	{
		expandedMap.push_back(-1);
	}

	for (int i = 0; i < expandedMap.size(); i++)
	{
		int num = expandedMap.at(i);
		if (num != -1)
		{
			int column = (i % 13);
			int row = (i - column) / 13;
			astarObj.addCollision({ row, column - 1 });
		}
	}

}

void PathFinder::putNewStone(int newIndex, int playerColor)
{


	int column = (newIndex % 13);
	int row = (newIndex - column) / 13;

	std::vector<AStar::Vec2i> path = astarObj.findPath({ 0,0 }, { row, column - 1 });

	pathCooridnates.clear();
	for (auto& coordinate : path)
	{
		pathCooridnates.push_back(coordinate.x);
		pathCooridnates.push_back(coordinate.y);
	}

	//publish new path somewhere here

	//after completion
	astarObj.addCollision({ row, column - 1 });

}

void PathFinder::removeStone(int index)
{

	int column = (index % 13);
	int row = (index - column) / 13;

	std::vector<AStar::Vec2i> path;

	for (int i = 2; i < expandedMap.size(); i++)
	{
		if (expandedMap.at(i) == -1)
		{
			path = astarObj.findPath({ 0,0 }, { row, column - 1 });
			i = expandedMap.size();
		}

		if (i == 12) //keep space available near spawn
		{
			i += 3;
		}
		if (i >= 26) // don't put any dead robots near board
		{
			i += 65;
		}
	}

	// publish to controller

	//after completion
	astarObj.addCollision({ row, column - 1 });

}