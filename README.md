# The Bailouts Problem 🗺️

Author: Gabriel de Almeida Spadafora :spades:

## Introduction
This code was developed as the final project for the Intelligent Systems course at UTFPR. Throughout the development, some code was provided by the professor as a foundation for solving the problem with my own solution. Due to tight deadlines, the code is not fully organized. The solution achieved good performance in the exploration phase, clustering, neural network training, and classification. The area that needs improvement is the genetic algorithm. Feel free to analyze the solution and adapt it as you see fit.

## Project Overview
The Bailouts Problem involves deploying explorer agents to navigate an unknown map and locate victims with varying degrees of injury. After exploration, the collected data is analyzed to cluster victims and estimate their severity, followed by planning rescue missions using rescuers. The project encompasses exploration, data analysis, clustering, severity estimation using machine learning models, and route optimization via a genetic algorithm.

Below is an overview of the project:
<p align="center">
<img src="https://github.com/GabrielSpdf/SistemasInteligentes/blob/main/assets/overview.jpg" width="350">
</p>

### Explore, Analyze, and Rescue
#### :memo: Exploration Phase
The problem involves navigating a map containing victims with varying degrees of injury. The goal is to explore the map using four explorer agents who have no prior information about the terrain, aiming to find as many victims as possible. All explorers start from a base location and must return to the base before a time limit expires, bringing back the individual maps they have discovered.

#### 🦋 Solution Approach
My solution was to distribute the agents equally across the map to maximize the diversity of their search regions. This strategy was affectionately nicknamed the "Butterfly Strategy" due to the pattern in which the agents spread out over the map, as illustrated below.

<p align="center">
<img src="https://github.com/GabrielSpdf/SistemasInteligentes/blob/main/assets/mov.jpg" width="350">
</p>

#### :mag: Analysis and Rescue Phase
After the explorers return to base, they provide the maps they have explored. The objective is to merge these individual maps into a single comprehensive map. Following this, the victims on the map are clustered into groups to assist in allocating them to the four rescuers. Additionally, the best route for each rescuer must be determined using a genetic algorithm.
#### :mailbox_with_no_mail: Clustering Solution
I used the K-Means++ algorithm for clustering, setting the number of clusters to four to correspond with the number of rescuer agents.

> [!NOTE]
> There is room for improvement in this approach. For example, the elbow method could be used to more precisely determine the ideal number of clusters, or the distribution logic could be implemented based on victim severity and rescuer time constraints.

#### :syringe: Severity Classification

After clustering, I implemented a neural network and a classifier to approximate the severity of each victim based on certain parameters. The neural network used was a Multi-Layer Perceptron (MLP), and the classifier was XGBoost. Both were implemented using Bayesian Optimization techniques.

Using the estimated victim severities, I adjusted the centroid of each cluster to be closer to the more severely injured victims. This was intended to aid the genetic algorithm in optimizing the rescue score, as the scoring equation assigns greater weight to rescuing more severely injured victims.

Below is a overview of the proposed idea:
<p align="center">
<img src="https://github.com/GabrielSpdf/SistemasInteligentes/blob/main/assets/clustering.jpg" width="350">
</p>

#### :ambulance: Genetic Algorithm for Route Optimization

The genetic algorithm I developed used the A* search algorithm, taking into account factors such as time, distance to the victim, victim severity, and distance to the cluster centroid (since centroids were adjusted to be closer to more severely injured victims).

#### :bar_chart: Results

The results indicated strong performance in the exploration phase, victim clustering, and severity classification using the neural network and classifier. Unfortunately, since the genetic algorithm is the main driver for rescuing victims (as it determines the rescue sequence for the rescuers), there is significant room for improvement in this area. Enhancing the genetic algorithm could substantially increase the overall effectiveness of the solution.

#### :chart_with_upwards_trend: Future Improvements
- Clustering Methods: I plan to explore other clustering methods and logic to improve the grouping of victims.
- Genetic Algorithm Optimization: I intend to refine the genetic algorithm by testing different search algorithms, adjusting parameters, and improving code efficiency to reduce its current complexity.

#### :mortar_board: Acknowledgments

I would like to thank Professor Cesar Augusto Tacla for the proposed project and for providing the initial codebase available at [VictimSim2](https://github.com/tacla/VictimSim2).
