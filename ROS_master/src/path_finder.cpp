
#include "ros/ros.h"
#include "AStar.hpp"
#include "std_msgs/Int16MultiArray.h"


AStar::Generator generator;
ros::Publisher path_pub;

void updateMap(const std_msgs::Int16MultiArray::ConstPtr& msg);
void calculateMove(const std_msgs::Int16MultiArray::ConstPtr& msg);


int main(int argc, char **argv)
{
  generator.setWorldSize({21,19});

  ros::init(argc, argv, "path_finder");
  ros::NodeHandle nh;
  ros::Subscriber map_sub = nh.subscribe("map", 1000, updateMap);
  ros::Subscriber map_sub = nh.subscribe("move", 1000, calculateMove);
  path_pub = nh.advertise<std_msgs::Int16MultiArray>("path", 1000);
  






  return 0;
}

void updateMap(const std_msgs::Int16MultiArray::ConstPtr& msg)
{
  auto arr = msg->data;
  
  for (int i = 0; i < 21; i++)
  {
    for (int j = 0; i < 19; j++)
    {
      if (arr.at( (i*21) + j) != 0)
      {
        generator.addCollision({i,j});
      }
      else
      {
        generator.removeCollision({i,j});
      }
    }
  }
}


void calculateMove(const std_msgs::Int16MultiArray::ConstPtr& msg)
{
  auto arr = msg->data;
  auto path = generator.findPath({arr.at(0), arr.at(1)}, {arr.at(2), arr.at(3)});
  std_msgs::Int16MultiArray pathArray;

  pathArray.data.clear();

  for (int i = 0; i < path.size(); i++)
  {
    pathArray.data.at(i) = path.at(i).x;
    pathArray.data.at(i+1) = path.at(i).y;
  }

  path_pub.publish(pathArray);

}
  
