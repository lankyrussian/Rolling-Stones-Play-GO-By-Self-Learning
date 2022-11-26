#include "PathPlanner.h"
#include <stdio.h>
#include <array>
#include <iostream>

int main()
{
	int map[25] =  {90, 90, 90, 90, 90,
					90, 90, 90, 90, 90,
					90, 90, 90, 90, 90,
					90, 90, 90, 90, 90,
					90, 90, 90, 90, 90, };

	for (int i = 0; i < 25; i++)
	{
		//std::cout << map[i];
		if ((i+1) % 5 == 0)
			std::cout << std::endl;
	}


	PathFinder pathObj;
	pathObj.initializeAndExpand(map);

	pathObj.putNewStone(13, 22);
	pathObj.removeStone(8);




	return 0;
}