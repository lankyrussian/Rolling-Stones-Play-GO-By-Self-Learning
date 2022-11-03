#include "PathPlanner.h"
#include <iostream>

PathFinder::PathFinder()
{}

PathFinder::~PathFinder()
{}

void PathFinder::initializeAndExpand(int newMap[25])
{
	//initialize or subscribe to map 

	astarObj.setWorldSize({ 9,13 });
	astarObj.setDiagonalMovement(false);


	for (int i = 0; i < 25; i++)
		map[i] = newMap[i];

	expandedMap.clear();
	for (int i = 0; i < 26; i++)
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
	for (int i = 0; i < 26; i++)
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
	if (newIndex > 24)
		return;

	int rowCount = newIndex / 5;
	int expandedIndex = 28 + (newIndex * 2) + (rowCount * 3);

	int column = (expandedIndex % 13);
	int row = (expandedIndex - column) / 13;

	expandedMap.at((row*13) + column) = playerColor;

	std::vector<AStar::Vec2i> path = astarObj.findPath({ row, column }, { 0,0 });

	pathCooridnates.clear();
	for (auto& coordinate : path)
	{
		pathCooridnates.push_back(coordinate.x);
		pathCooridnates.push_back(coordinate.y);
	}

	for (int i = 0; i < pathCooridnates.size(); i++)
	{
		std::cout << pathCooridnates.at(i);
		if ((i+1) % 2 == 0)
			std::cout << std::endl;
	}

	//publish new path somewhere here

	//after completion
	astarObj.addCollision({ row, column });

	for (int i = 0; i < expandedMap.size(); i++)
	{
		std::cout << expandedMap.at(i) << ' ';
		if ((i + 1) % 13 == 0)
			std::cout << std::endl;
	}


}

void PathFinder::removeStone(int index)
{
	int rowCount = index / 5;
	int expandedIndex = 28 + (index * 2) + (rowCount * 3);

	int deadRow, deadColumn;

	int column = (expandedIndex % 13);
	int row = (expandedIndex - column) / 13;

	std::vector<AStar::Vec2i> path;

	for (int i = 2; i < expandedMap.size(); i++)
	{
		if (expandedMap.at(i) == -1)
		{
			deadColumn = (i % 13);
			deadRow = (i - deadColumn) / 13;
			astarObj.removeCollision({ row, column }); //need to tell astar there's no collision where it's located

			path = astarObj.findPath( {deadRow, deadColumn}, { row, column });
			//these need to be done AFTER the motion is completed
			astarObj.addCollision({ deadRow, deadColumn });

			//break
			i = (int)expandedMap.size();
			

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

	pathCooridnates.clear();
	for (auto& coordinate : path)
	{
		pathCooridnates.push_back(coordinate.x);
		pathCooridnates.push_back(coordinate.y);
	}

	for (int i = 0; i < pathCooridnates.size(); i++)
	{
		std::cout << pathCooridnates.at(i);
		if ((i + 1) % 2 == 0)
			std::cout << std::endl;
	}


	// publish path to controller


}