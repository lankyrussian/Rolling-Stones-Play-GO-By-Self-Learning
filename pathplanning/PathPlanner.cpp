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
	InitializeAndExpand();
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
	printf("Press Enter to quit...\n");
	getchar();
	mosquitto_loop_stop(_mqtt, true);

	mosquitto_disconnect(_mqtt);
	mosquitto_destroy(_mqtt);
	mosquitto_lib_cleanup();
}

void PathFinder::OnConnect(struct mosquitto *msqt, void *obj, int reason)
{
	PathFinder* pfPtr = static_cast<PathFinder *>(obj);
	std::cout << "Connected to broker. Reason:" << mosquitto_reason_string(reason) << std::endl;
	mosquitto_subscribe(pfPtr->_mqtt, NULL, "/gomove", 2);
	std::cout << "Subscribed to /gomove" << std::endl;
}

void PathFinder::OnMessage(struct mosquitto * msqt, void * obj, const struct mosquitto_message * msg)
{
	PathFinder* pfPtr = static_cast<PathFinder *>(obj);
	std::cout << "Message received on topic:" << msg->topic << std::endl;

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

void PathFinder::OnPublish(struct mosquitto *msqt, void *obj, int mid)
{
	std::cout << "Message was published: " << mid << std::endl;
}


void PathFinder::InitializeAndExpand()
{
	//initialize or subscribe to map 

	astarObj.setWorldSize({ 13,13 });
	astarObj.setDiagonalMovement(false);

	std::vector<int> tempVect((rowSize*columnSize), 0);
	expandedMap = tempVect;
}

void PathFinder::PutNewStone(int newIndex, int playerColor)
{
	if (newIndex > 24)
		return;

	int rowCount = newIndex / 5;
	int expandedIndex = 28 + (newIndex * 2) + (rowCount * 16);

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

	std::cout << "Adding Stone: " << std::endl;
	for (int i = 0; i < pathCooridnates.size(); i++)
	{
		std::cout << pathCooridnates.at(i);
		if ((i+1) % 2 == 0)
			std::cout << std::endl;
	}

	int rc = mosquitto_publish(_mqtt, NULL, "gopath", (pathCooridnates.size() * sizeof(int) ), pathCooridnates.data(), 2, false);
	if(rc != MOSQ_ERR_SUCCESS){
		std::cout << "Error publishing: " << mosquitto_strerror(rc) << std::endl;
	}

	//after completion
	astarObj.addCollision({ row, column });

}

void PathFinder::RemoveStone(int index)
{
	int rowCount = index / 5;
	int expandedIndex = 28 + (index * 2) + (rowCount * 16);

	int deadRow, deadColumn;

	int column = (expandedIndex % 13);
	int row = (expandedIndex - column) / 13;

	std::vector<AStar::Vec2i> path;

	for (int i = 2; i < expandedMap.size(); i++)
	{
		if (expandedMap.at(i) == 0)
		{
			deadColumn = (i % 13);
			deadRow = (i - deadColumn) / 13;
			astarObj.removeCollision({ row, column }); //need to tell astar there's no collision where it's located

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

	std::cout << "Removing Stone: " << std::endl;
	for (int i = 0; i < pathCooridnates.size(); i++)
	{
		std::cout << pathCooridnates.at(i);
		if ((i + 1) % 2 == 0)
			std::cout << std::endl;
	}


	// publish
	int rc = mosquitto_publish(_mqtt, NULL, "/gopath", (pathCooridnates.size() * sizeof(int) ), pathCooridnates.data(), 2, false);
	if(rc != MOSQ_ERR_SUCCESS){
		std::cout << "Error publishing: " << mosquitto_strerror(rc) << std::endl;
	}

	astarObj.addCollision({ deadRow, deadColumn });

}
