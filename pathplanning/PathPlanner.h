#include <stdio.h>
#include <vector>
#include <algorithm>
#include "AStar.h"
#include <mosquitto.h>
#include <mutex>

class PathFinder
{
public:
	PathFinder();
	~PathFinder();

	static void OnConnect(struct mosquitto* msqt, void* obj, int reason);
	static void OnMessage(struct mosquitto * msqt, void * obj, const struct mosquitto_message * msg);
	static void OnPublish(struct mosquitto *msqt, void *obj, int mid);


	void InitializeAndExpand(int* map, int len);
	void PutNewStone(int newIndex, int playerColor);
	void RemoveStone(int index);
	void InitializeMqtt();
	void MqttLoop();

private:
	const int rowSize = 15;
	const int columnSize = 15;
	bool mapInitialized = false;
	int map[25];
	std::vector<int> expandedMap;
	AStar::Generator astarObj;
	std::vector<int> pathCooridnates;
	std::mutex m;
	struct mosquitto* _mqtt;
};

