#include "PathPlanner.h"
#include <iostream>


PathFinder::PathFinder()
{
	mosquitto_lib_init();
	_mqtt = mosquitto_new(NULL, true, this);
	if (_mqtt == NULL)
	{
		std::cout << "Failed to create an mqtt instance";
		return;
	}
	InitializeMqtt();
}

PathFinder::~PathFinder()
{}


void PathFinder::InitializeMqtt()
{
	mosquitto_connect_callback_set(_mqtt, OnConnect);
	mosquitto_message_callback_set(_mqtt, OnMessage);
	mosquitto_publish_callback_set(_mqtt, OnPublish);
	MqttLoop();
}

void PathFinder::MqttLoop()
{
	int rc = mosquitto_connect(_mqtt, "0.0.0.0", 1883, 10);
	if(rc) {
		std::cout << "Error establishing connection: " << mosquitto_strerror(rc) << std::endl;
		return;
	}
	mosquitto_loop_start(_mqtt);
	printf("Started Path Planner...\n");
	while(1)
    {
        getchar();
    }
//	mosquitto_loop_stop(_mqtt, true);
//
//	mosquitto_disconnect(_mqtt);
//	mosquitto_destroy(_mqtt);
//	mosquitto_lib_cleanup();
}

void PathFinder::OnConnect(struct mosquitto *msqt, void *obj, int reason)
{
	PathFinder* pfPtr = static_cast<PathFinder *>(obj);
	std::cout << "Connected to broker. Reason:" << mosquitto_reason_string(reason) << std::endl;
	mosquitto_subscribe(pfPtr->_mqtt, NULL, "/gomove", 2);
	std::cout << "Subscribed to /gomove" << std::endl;
	mosquitto_subscribe(pfPtr->_mqtt, NULL, "/gomap", 2);
	std::cout << "Subscribed to /gomap" << std::endl;

}	

void PathFinder::OnMessage(struct mosquitto * msqt, void * obj, const struct mosquitto_message * msg)
{
	PathFinder* pfPtr = static_cast<PathFinder *>(obj);
	std::cout << "Message received on topic:" << msg->topic << std::endl;
	pfPtr->m.lock();
	if ((std::string)msg->topic == "/gomove")
	{ 
		if (msg->payloadlen != 8)
		{
			std::cout << "Message length is invalid, expected 8bytes(2 ints), recieved " << msg->payloadlen << "bytes.";
			return;
		}
		else
		{
			int* msgArr = static_cast<int*>(msg->payload);
			if (msgArr[1] != 0)
			{
				pfPtr->PutNewStone(msgArr[0], msgArr[1]);
			}
			else
			{
				pfPtr->RemoveStone(msgArr[0]);

			}
		}
	}
	else if ((std::string)msg->topic == "/gomap")
	{
		if (msg->payloadlen != 900)
		{
			std::cout << "Message length is invalid, expected 900bytes(15x15 ints), recieved " << msg->payloadlen << "bytes.";
			return;
		}
		int* msgArr = static_cast<int*>(msg->payload);
		pfPtr->mapInitialized = true;
		pfPtr->InitializeAndExpand(msgArr, msg->payloadlen / 4);

	}
	pfPtr->m.unlock();
}

void PathFinder::OnPublish(struct mosquitto *msqt, void *obj, int mid)
{
	std::cout << "Message was published: " << mid << std::endl;
}

void display(int* map, int length)
{
    for (int i = 0; i < length; i++)
    {
        std::cout << map[i] << " ";
        if (i % 15 == 14)
        {
            std::cout << std::endl;
        }
    }
}

void PathFinder::InitializeAndExpand(int* map, int len)
{
	//initialize or subscribe to map 

	astarObj.setWorldSize({ 15,15 });
	astarObj.clearCollisions();

	//init internal data struct
	expandedMap.clear();
	for (int i = 0; i < len; i++)
	{
		expandedMap.push_back(map[i]);
	}
	// display
	display(map, len);

	//init astar map
	for (int i = 0; i < expandedMap.size(); i++)
	{
		int num = expandedMap.at(i);
		if (num != 0)
		{
			int column = (i % 15);
			int row = (i - column) / 15;
			astarObj.addCollision({ row, column });
		}
	}

}

void PathFinder::PutNewStone(int newIndex, int playerColor)
{
	if (newIndex > 24 || mapInitialized == false)
		return;

	int rowCount = newIndex / 5;
	int expandedIndex = 48 + (newIndex * 2) + (rowCount * 20);

	int column = (expandedIndex % 15);
	int row = (expandedIndex - column) / 15;


	std::vector<int> availableStonesIndex;
	for(int i = 0; i < expandedMap.size(); i++)
	{
		int currRow = i / 15;
		int currColumn = i % 15;
		// can't use stones from the board as new stones
		if (currRow > 2 && currRow < 12 && currColumn > 2 && currColumn < 12){
           continue;
        }
        int var2 = expandedMap.at(i);
        if (var2 == 1)
            availableStonesIndex.push_back(i);
	}

	std::vector<AStar::Vec2i> path;
	int PathWeight = INT32_MAX;
	int startCol, startRow;
	for(int i = 0; i < availableStonesIndex.size(); i++)
	{	
		int tempColumn = (availableStonesIndex.at(i) % 15);
		int tempRow = (availableStonesIndex.at(i) - tempColumn) / 15;
		std::cout << "considering: " << tempRow << " " << tempColumn << std::endl;
		astarObj.removeCollision({tempRow, tempColumn});
		std::vector<AStar::Vec2i> tempPath = astarObj.findPath({ tempRow, tempColumn }, { row , column });
		astarObj.addCollision({tempRow, tempColumn});
		int x = tempPath[0].x;
		int y = tempPath[0].y;
		int size = tempPath.size();
		int mainSize = path.size();

		if (x == row && y == column)
		{
			if (tempPath.size() < PathWeight)
			{
				path = tempPath;
				PathWeight = tempPath.size();
				startCol = tempColumn;
				startRow = tempRow;
			}
		}

	}
	if(PathWeight==INT32_MAX)
    {
        std::cout << "Error: No path found" << std::endl;
        display(expandedMap.data(), expandedMap.size());
        return;
    }

	pathCooridnates.clear();
	for (auto& coordinate : path)
	{
		pathCooridnates.push_back(coordinate.y);
		pathCooridnates.push_back(coordinate.x);
	}
	pathCooridnates.push_back(playerColor);
	std::reverse(pathCooridnates.begin(), pathCooridnates.end());
	for (int i = 0; i < pathCooridnates.size(); i++)
	{
		std::cout << pathCooridnates.at(i) << ' ';
		if (i % 2 == 0)
			std::cout << std::endl;
	}

	//after completion
	// new stone is added to map
	astarObj.addCollision({ row, column });
	expandedMap.at((row*15) + column) = 1;
    // remove stone's old position from the map
	astarObj.removeCollision({ startRow, startCol });
	expandedMap.at((startRow*15) + startCol) = 0;

	int rc = mosquitto_publish(_mqtt, NULL, "/gopath", (pathCooridnates.size() * sizeof(int) ), pathCooridnates.data(), 2, false);
	if(rc != MOSQ_ERR_SUCCESS){
		std::cout << "Error publishing: " << mosquitto_strerror(rc) << std::endl;
	}
}

void PathFinder::RemoveStone(int index)
{
	if (mapInitialized == false)
		return;
	
	
	int rowCount = index / 5;
	int expandedIndex = 48 + (index * 2) + (rowCount * 20);

	int column = (expandedIndex % 15);
	int row = (expandedIndex - column) / 15;

	int deadRow, deadColumn;
	std::vector<AStar::Vec2i> path;

	for (int i = 2; i < expandedMap.size(); i++)
	{
		if (expandedMap.at(i) == 0)
		{
			deadColumn = (i % 15);
			deadRow = (i - deadColumn) / 15;
			astarObj.removeCollision({ row, column }); //need to tell astar there's no collision where it's located
			expandedMap.at((row*15) + column) = 0;

			path = astarObj.findPath( {deadRow, deadColumn}, { row, column });

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

	std::cout << "Removing Stone" << std::endl;

    astarObj.addCollision({ deadRow, deadColumn });
	expandedMap.at((deadRow*15) + deadColumn) = 1;
	// publish
	int rc = mosquitto_publish(_mqtt, NULL, "/gopath", (pathCooridnates.size() * sizeof(int) ), pathCooridnates.data(), 2, false);
	if(rc != MOSQ_ERR_SUCCESS){
		std::cout << "Error publishing: " << mosquitto_strerror(rc) << std::endl;
	}

}
