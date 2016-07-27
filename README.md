# Traffic Simulator rules:
1. Each car employs a Intelligent Driving Model (https://en.wikipedia.org/wiki/Intelligent_driver_model). A car will accelerate or decelerate by the following rules:
  - the distance between its front car (if there is a car in front of the current car) or the intersection line (if the light is red).
  - the speed difference between the front car and the current car.
  - the speed cannot exceed the speed limit of each road.
2. A can cannot passes its front car. 
3. Each road has two directions and each direction has two lane. Cars can change to another lane.
4. A car that is going to turn right, it must be on the right-most lane and turn to the right-most lane on the right-turn road.
5. Traffic lights at each intersection change independently. Cars need to determine whether it can pass the intersection according to the traffic lights
6. Add cars into the map at each road that connect the border of the map at a poisson arrival with different lambda parameter.
