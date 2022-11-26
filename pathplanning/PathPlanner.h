#include <stdio.h>
#include <vector>
#include "AStar.h"
#include <mosquitto.h>

class PathFinder
{
public:
	PathFinder();
	~PathFinder();

	static void OnConnect(struct mosquitto* msqt, void* obj, int reason);
	static void OnMessage(struct mosquitto * msqt, void * obj, const struct mosquitto_message * msg);
	static void OnPublish(struct mosquitto *msqt, void *obj, int mid);


	void InitializeAndExpand();
	void PutNewStone(int newIndex, int playerColor);
	void RemoveStone(int index);
	void InitializeMqtt();
	void MqttLoop();

private:
	const int rowSize = 13;
	const int columnSize = 13;
	int map[25];
	std::vector<int> expandedMap;
	AStar::Generator astarObj;
	std::vector<int> pathCooridnates;
	struct mosquitto* _mqtt;
};

